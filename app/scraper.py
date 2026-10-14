import json
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import httpx

from app.config import settings


def parse_datatable_response(raw_text: str) -> List[Dict[str, Any]]:
    """Parse AjaxPro DataTable response into a list of dictionaries."""
    trimmed = raw_text.strip()
    prefix = "new Ajax.Web.DataTable("
    suffix = ");/*"

    if not (trimmed.startswith(prefix) and trimmed.endswith(suffix)):
        return []

    inner = trimmed[len(prefix):-len(suffix)]
    try:
        # Wrap inner arguments into a valid JSON array
        parsed = json.loads(f"[{inner}]")
    except json.JSONDecodeError:
        return []

    if len(parsed) < 2 or not isinstance(parsed[0], list) or not isinstance(parsed[1], list):
        return []

    columns = [col[0] for col in parsed[0] if isinstance(col, list) and len(col) > 0]
    rows = parsed[1]

    results: List[Dict[str, Any]] = []
    for row in rows:
        if isinstance(row, list) and len(row) == len(columns):
            results.append(dict(zip(columns, row)))

    return results


def parse_publicacoes_response(raw_text: str, base_url: str) -> List[Dict[str, Any]]:
    """Parse HTML publications returned by AjaxPro GetPublicacoes endpoint."""
    trimmed = raw_text.strip()
    if trimmed.endswith(";/*"):
        trimmed = trimmed[:-len(";/*")].strip()

    try:
        html_content = json.loads(trimmed)
    except json.JSONDecodeError:
        html_content = trimmed

    if not isinstance(html_content, str) or not html_content.strip():
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    publicacoes: List[Dict[str, Any]] = []

    for item in soup.find_all("li", class_="list-group-item"):
        link_tag = item.find("a")
        if not link_tag:
            continue

        raw_title = link_tag.get_text(strip=True)
        href = link_tag.get("href", "")
        file_url = urljoin(base_url, href) if href else None

        date_match = re.match(r"^(\d{2}/\d{2}/\d{4})\s*-\s*(.+)$", raw_title)
        if date_match:
            data_pub = date_match.group(1)
            titulo = date_match.group(2)
        else:
            data_pub = None
            titulo = raw_title

        publicacoes.append({
            "titulo": titulo,
            "data_publicacao": data_pub,
            "url_arquivo": file_url
        })

    return publicacoes


class PrefeituraSeteLagoasScraper:
    def __init__(
        self,
        base_url: str = settings.base_portal_url,
        timeout: float = settings.request_timeout,
        user_agent: str = settings.user_agent,
        client: Optional[httpx.Client] = None
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent
        self._client = client
        self.lis_handler_path: Optional[str] = None
        self.vis_handler_path: Optional[str] = None

    def _get_client(self) -> httpx.Client:
        if self._client is not None:
            return self._client
        return httpx.Client(
            headers={"User-Agent": self.user_agent},
            timeout=self.timeout,
            follow_redirects=True
        )

    def discover_lis_handler(self, client: httpx.Client) -> str:
        """Locate current dynamic ASHX handler for process listing."""
        if self.lis_handler_path:
            return self.lis_handler_path

        url = f"{self.base_url}/processos-seletivos"
        response = client.get(url)
        response.raise_for_status()

        match = re.search(r"/ajaxpro/proc_sel_lis,[^\"'\s]+\.ashx", response.text)
        if match:
            self.lis_handler_path = match.group(0)
            return self.lis_handler_path

        # Fallback to standard path if pattern not detected
        self.lis_handler_path = "/ajaxpro/proc_sel_lis,App_Web_dgw4kxhx.ashx"
        return self.lis_handler_path

    def discover_vis_handler(self, client: httpx.Client, sample_cd: int) -> str:
        """Locate current dynamic ASHX handler for process details."""
        if self.vis_handler_path:
            return self.vis_handler_path

        url = f"{self.base_url}/proc_sel_vis.aspx?cd={sample_cd}"
        response = client.get(url)
        response.raise_for_status()

        match = re.search(r"/ajaxpro/proc_sel_vis,[^\"'\s]+\.ashx", response.text)
        if match:
            self.vis_handler_path = match.group(0)
            return self.vis_handler_path

        # Fallback to standard path if pattern not detected
        self.vis_handler_path = "/ajaxpro/proc_sel_vis,App_Web_1sb10zcy.ashx"
        return self.vis_handler_path

    def fetch_processos(
        self,
        page: int = 0,
        size: int = 20,
        cd_tipo: Optional[int] = None,
        cd_situacao: Optional[int] = None,
        nu_ano: Optional[int] = None,
        keyword: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        client = self._get_client()
        should_close = self._client is None

        try:
            handler = self.discover_lis_handler(client)
            endpoint = f"{self.base_url}{handler}"

            payload = {
                "Page": page,
                "Size": size,
                "cdTipo": str(cd_tipo) if cd_tipo is not None else None,
                "nuProcSeletivo": None,
                "nuAno": nu_ano,
                "palavraChave": keyword,
                "cdUnidade": None,
                "cdSituacao": cd_situacao,
                "dmOrdenacao": 1
            }

            headers = {
                "Content-Type": "text/plain; charset=utf-8",
                "X-AjaxPro-Method": "GetListaDados"
            }

            response = client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return parse_datatable_response(response.text)
        finally:
            if should_close:
                client.close()

    def fetch_publicacoes(self, cd_proc_seletivo: int) -> List[Dict[str, Any]]:
        client = self._get_client()
        should_close = self._client is None

        try:
            handler = self.discover_vis_handler(client, cd_proc_seletivo)
            endpoint = f"{self.base_url}{handler}"

            payload = {
                "cdProcSeletivo": cd_proc_seletivo,
                "dmOpcaoExibicao": 1
            }

            headers = {
                "Content-Type": "text/plain; charset=utf-8",
                "X-AjaxPro-Method": "GetPublicacoes"
            }

            response = client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return parse_publicacoes_response(response.text, self.base_url)
        finally:
            if should_close:
                client.close()
