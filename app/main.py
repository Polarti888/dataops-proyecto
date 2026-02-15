#!/usr/bin/env python3
"""
Cálculo de comisiones - Python 3.11
"""

from datetime import date
from pathlib import Path
from decimal import Decimal
import json, os, sys, smtplib
import pandas as pd
import psycopg2
from typing import Union

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header

# 1. Cargar configuración
def load_config(path: Union[str, Path, None] = None) -> dict:
    path = Path(path) if path else Path(__file__).with_name("config.json")
    if not path.exists():
        print(f"Error: Archivo de configuración {path} no encontrado.")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))

CFG = load_config(os.getenv("CONFIG_FILE"))
DB_CFG = CFG["db"]
SMTP_CFG = CFG["smtp"]
PATHS = CFG["paths"]
REPORT = CFG["report"]

# 2. Función para enviar correo
def send_mail(to: str, subj: str, html: str, attachment: Path) -> None:
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_CFG["sender_email"]
        msg["To"] = to
        msg["Subject"] = str(Header(subj, "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        with open(attachment, "rb") as fh:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(fh.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{attachment.name}"')
        msg.attach(part)
        
        with smtplib.SMTP(SMTP_CFG["server"], SMTP_CFG["port"]) as smtp:
            smtp.starttls()
            smtp.login(SMTP_CFG["user"], SMTP_CFG["password"])
            smtp.send_message(msg)
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error crítico al enviar el correo: {e}")
        sys.exit(1)

# 3. Script principal
def main() -> None:
    periodo = date.today().strftime("%Y%m")
    csv_dir = Path(PATHS.get("csv_dir", "."))
    csv_file = csv_dir / f"ComisionEmpleados_V1_{periodo}.csv"

    print(f"Iniciando proceso. Buscando archivo: {csv_file}")

    if not csv_file.exists():
        print(f"No hay comisiones para {periodo}. Fin.")
        sys.exit(0)

    print("Archivo detectado. Leyendo CSV...")
    try:
        csv_df = pd.read_csv(csv_file, sep=";")
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        sys.exit(1)

    print("Conectando a PostgreSQL...")
    try:
        with psycopg2.connect(**DB_CFG) as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM rrhh.empleado;")
            db_df = pd.DataFrame(cur.fetchall(), columns=[c[0] for c in cur.description])
        print("Conexión a base de datos exitosa.")
    except Exception as e:
        print(f"Error de conexión a la base de datos: {e}")
        sys.exit(1)

    print("Uniendo datos y calculando comisiones...")
    merged = csv_df.merge(db_df, on="empleado_id")

    num_cols = ["mnt_salario", "Comisión", "mnt_tope_comision"]
    merged[num_cols] = (merged[num_cols]
                        .apply(pd.to_numeric, errors="coerce")
                        .fillna(0))

    # Se convierte a string primero para evitar errores de redondeo de float en pandas
    merged["comision_calculada"] = merged.apply(
        lambda r: min(
            Decimal(str(r.mnt_salario)) * Decimal("0.10") + Decimal(str(r.Comisión)),
            Decimal(str(r.mnt_tope_comision))
        ),
        axis=1
    )
    
    excel_out = Path(PATHS["excel"])
    print(f"Guardando resultados en {excel_out}...")
    try:
        merged.to_excel(excel_out, index=False, engine="openpyxl")
    except Exception as e:
        print(f"Error al guardar el archivo Excel: {e}")
        sys.exit(1)

    print("Preparando envío de correo...")
    send_mail(REPORT["to"], REPORT["subject"], REPORT["body_html"], excel_out)
    
    print("Proceso finalizado con éxito.")

if __name__ == "__main__":
    main()
