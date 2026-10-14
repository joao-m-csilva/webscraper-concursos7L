import argparse
import sys
from app.database import SessionLocal, init_db
from app.scraper import PrefeituraSeteLagoasScraper
from app.service import sync_concursos


def parse_arguments(args=None):
    parser = argparse.ArgumentParser(
        description="Sync concursos and selecoes from Prefeitura de Sete Lagoas"
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of pages to scrape (default: 1)"
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=20,
        help="Number of items per page (default: 20)"
    )
    parser.add_argument(
        "--tipo-id",
        type=int,
        default=None,
        help="Filter by specific type ID (1: Concurso, 2: Simplificado, etc.)"
    )
    parser.add_argument(
        "--no-details",
        action="store_true",
        help="Skip fetching attached publications and files"
    )
    return parser.parse_args(args)


def main(args=None) -> int:
    parsed = parse_arguments(args)
    init_db()
    db = SessionLocal()
    scraper = PrefeituraSeteLagoasScraper()

    try:
        concursos, publicacoes = sync_concursos(
            db=db,
            scraper=scraper,
            pages=parsed.pages,
            page_size=parsed.page_size,
            cd_tipo=parsed.tipo_id,
            fetch_details=not parsed.no_details
        )
        print(f"Sync completed: {concursos} items processed, {publicacoes} publications added.")
        return 0
    except Exception as exc:
        print(f"Error during synchronization: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
