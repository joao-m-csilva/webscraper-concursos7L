import pytest
from run_scraper import main, parse_arguments


def test_parse_arguments_defaults():
    args = parse_arguments([])
    assert args.pages == 1
    assert args.page_size == 20
    assert args.tipo_id is None
    assert args.no_details is False


def test_parse_arguments_custom():
    args = parse_arguments(["--pages", "3", "--page-size", "10", "--tipo-id", "1", "--no-details"])
    assert args.pages == 3
    assert args.page_size == 10
    assert args.tipo_id == 1
    assert args.no_details is True


def test_main_cli_success(monkeypatch):
    import run_scraper

    def dummy_sync(*args, **kwargs):
        return 2, 3

    monkeypatch.setattr(run_scraper, "sync_concursos", dummy_sync)
    result = main(["--pages", "1"])
    assert result == 0


def test_main_cli_failure(monkeypatch):
    import run_scraper

    def failing_sync(*args, **kwargs):
        raise RuntimeError("Network error")

    monkeypatch.setattr(run_scraper, "sync_concursos", failing_sync)
    result = main(["--pages", "1"])
    assert result == 1
