import httpx
import pytest
from app.scraper import (
    PrefeituraSeteLagoasScraper,
    parse_datatable_response,
    parse_publicacoes_response,
)


def test_parse_datatable_response_valid():
    raw = (
        'new Ajax.Web.DataTable([["CDPROCSELETIVO","System.Decimal"],["NMTITULO","System.String"]],'
        '[[101,"Concurso Geral"],[102,"Processo Saude"]]);/*'
    )
    results = parse_datatable_response(raw)
    assert len(results) == 2
    assert results[0]["CDPROCSELETIVO"] == 101
    assert results[0]["NMTITULO"] == "Concurso Geral"
    assert results[1]["CDPROCSELETIVO"] == 102
    assert results[1]["NMTITULO"] == "Processo Saude"


def test_parse_datatable_response_empty():
    raw = 'new Ajax.Web.DataTable([["CDPROCSELETIVO","System.Decimal"]],[]);/*'
    results = parse_datatable_response(raw)
    assert results == []


def test_parse_datatable_response_invalid_wrapper():
    assert parse_datatable_response("random string") == []
    assert parse_datatable_response("new Ajax.Web.DataTable([bad json]);/*") == []
    assert parse_datatable_response("") == []


def test_parse_datatable_response_row_mismatch():
    raw = 'new Ajax.Web.DataTable([["COL1","System.String"],["COL2","System.String"]],[["only_one"]]);/*'
    results = parse_datatable_response(raw)
    assert results == []


def test_parse_publicacoes_response_valid():
    html_raw = (
        '"<ul class=\\"list-group\\">'
        '<li class=\\"list-group-item\\">'
        '<div><a href=\\"abrir_arquivo.aspx?id=123\\">10/10/2026 - Edital de Abertura</a></div>'
        '</li>'
        '</ul>";/*'
    )
    pubs = parse_publicacoes_response(html_raw, "https://www.setelagoas.mg.gov.br")
    assert len(pubs) == 1
    assert pubs[0]["titulo"] == "Edital de Abertura"
    assert pubs[0]["data_publicacao"] == "10/10/2026"
    assert pubs[0]["url_arquivo"] == "https://www.setelagoas.mg.gov.br/abrir_arquivo.aspx?id=123"


def test_parse_publicacoes_response_without_date():
    html_raw = (
        '"<ul class=\\"list-group\\">'
        '<li class=\\"list-group-item\\">'
        '<div><a href=\\"/docs/anexo.pdf\\">Lista de Homologacao Final</a></div>'
        '</li>'
        '</ul>";/*'
    )
    pubs = parse_publicacoes_response(html_raw, "https://www.setelagoas.mg.gov.br")
    assert len(pubs) == 1
    assert pubs[0]["titulo"] == "Lista de Homologacao Final"
    assert pubs[0]["data_publicacao"] is None
    assert pubs[0]["url_arquivo"] == "https://www.setelagoas.mg.gov.br/docs/anexo.pdf"


def test_parse_publicacoes_response_empty():
    assert parse_publicacoes_response('""', "https://www.setelagoas.mg.gov.br") == []
    assert parse_publicacoes_response('";/*', "https://www.setelagoas.mg.gov.br") == []
    assert parse_publicacoes_response("", "https://www.setelagoas.mg.gov.br") == []


def test_scraper_fetch_processos_mock(monkeypatch):
    sample_response = (
        'new Ajax.Web.DataTable([["CDPROCSELETIVO","System.Decimal"],["CDTIPO","System.Decimal"],'
        '["NUPROCSELETIVO","System.Int32"],["NUANOPROCSELETIVO","System.Int32"],'
        '["NMTITULO","System.String"],["CDSITUACAO","System.Decimal"],["NMSITUACAO","System.String"],'
        '["NMUNIDADE","System.String"],["STDESTAQUE","System.Boolean"]],'
        '[[500,1,1,2026,"CONCURSO PUBLICO MUNICIPAL",2,"Em andamento","Educacao",false]]);/*'
    )

    def handler(request: httpx.Request):
        if "processos-seletivos" in str(request.url):
            return httpx.Response(200, text='<script src="/ajaxpro/proc_sel_lis,TestHandler.ashx"></script>')
        return httpx.Response(200, text=sample_response)

    transport = httpx.MockTransport(handler)
    mock_client = httpx.Client(transport=transport)

    scraper = PrefeituraSeteLagoasScraper(client=mock_client)
    items = scraper.fetch_processos(page=0, size=10, cd_tipo=1)

    assert len(items) == 1
    assert items[0]["CDPROCSELETIVO"] == 500
    assert items[0]["NMTITULO"] == "CONCURSO PUBLICO MUNICIPAL"
    assert items[0]["NMSITUACAO"] == "Em andamento"


def test_scraper_fetch_publicacoes_mock(monkeypatch):
    pub_html = (
        '"<ul class=\\"list-group\\">'
        '<li class=\\"list-group-item\\">'
        '<div><a href=\\"abrir_arquivo.aspx?id=99\\">05/05/2026 - Convocacao de Aprovados</a></div>'
        '</li>'
        '</ul>";/*'
    )

    def handler(request: httpx.Request):
        if "proc_sel_vis.aspx" in str(request.url):
            return httpx.Response(200, text='<script src="/ajaxpro/proc_sel_vis,VisTest.ashx"></script>')
        return httpx.Response(200, text=pub_html)

    transport = httpx.MockTransport(handler)
    mock_client = httpx.Client(transport=transport)

    scraper = PrefeituraSeteLagoasScraper(client=mock_client)
    pubs = scraper.fetch_publicacoes(500)

    assert len(pubs) == 1
    assert pubs[0]["titulo"] == "Convocacao de Aprovados"
    assert pubs[0]["data_publicacao"] == "05/05/2026"
    assert "abrir_arquivo.aspx?id=99" in pubs[0]["url_arquivo"]
