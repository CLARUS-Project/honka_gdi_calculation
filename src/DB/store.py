import psycopg2
import os

def store_gdi(pilot, data):
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_GDI_DATABASE"),
        user=os.getenv("POSTGRES_GDI_USERNAME"),
        password=os.getenv("POSTGRES_GDI_PASSWORD"),
        host=os.getenv("POSTGRES_GDI_HOST"),
        port=os.getenv("POSTGRES_GDI_PORT")
    )
    cur = conn.cursor()

    # Insertar el resultado global del GDI
    cur.execute(
        "INSERT INTO gdi_results (pilot, gdi_value) VALUES (%s, %s) RETURNING id",
        (pilot, data["gdi"])
    )
    gdi_result_id = cur.fetchone()[0]

    # Insertar cada contribución individual
    for indicator in data["gdi_indicators"]:
        cur.execute(
            """
            INSERT INTO gdi_contributions (
                gdi_result_id,
                indicator_name,
                hierarchy_level,
                impact_type,
                contribution
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (
                gdi_result_id,
                indicator["name"],
                indicator["hierarchy_level"],
                indicator["impact_type"],
                indicator["contribution"]
            )
        )

    conn.commit()
    cur.close()
    conn.close()
