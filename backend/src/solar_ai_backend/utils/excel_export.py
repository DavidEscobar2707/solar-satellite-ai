from __future__ import annotations

from typing import List, Dict, Any
import base64
import csv
from io import BytesIO, StringIO
from openpyxl import Workbook


def leads_to_excel_b64(leads: List[Dict[str, Any]], *, filename: str = "leads.xlsx") -> Dict[str, str]:
    """Create an XLSX workbook from leads and return base64 + suggested filename.

    Columns are chosen for readability and Lovable ingestion (flat, simple types).
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Leads"

    headers = [
        "address",
        "lat",
        "lng",
        "zpid",
        "price",
        "beds",
        "baths",
        "livingArea",
        "lotSize",
        "image_url",
        "backyard_status",
        "backyard_confidence",
        "notes",
        "lead_score",
    ]
    ws.append(headers)

    for lead in leads:
        address = lead.get("address")
        coords = lead.get("coordinates") or {}
        z = lead.get("zillow") or {}
        img = lead.get("imagery") or {}
        v = lead.get("vision") or {}

        ws.append([
            address,
            (coords.get("lat")),
            (coords.get("lng")),
            (z.get("zpid")),
            (z.get("price")),
            (z.get("beds")),
            (z.get("baths")),
            (z.get("livingArea")),
            (z.get("lotSize")),
            (img.get("image_url")),
            (v.get("backyard_status")),
            (v.get("backyard_confidence")),
            (v.get("notes")),
            (lead.get("lead_score")),
        ])

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    payload_b64 = base64.b64encode(bio.read()).decode("utf-8")
    return {"filename": filename, "base64": payload_b64}


def leads_to_excel_bytes(leads: List[Dict[str, Any]]) -> bytes:
    """Create an XLSX workbook from leads and return raw bytes."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Leads"

    headers = [
        "address",
        "lat",
        "lng",
        "zpid",
        "price",
        "beds",
        "baths",
        "livingArea",
        "lotSize",
        "image_url",
        "backyard_status",
        "backyard_confidence",
        "notes",
        "lead_score",
    ]
    ws.append(headers)

    for lead in leads:
        address = lead.get("address")
        coords = lead.get("coordinates") or {}
        z = lead.get("zillow") or {}
        img = lead.get("imagery") or {}
        v = lead.get("vision") or {}

        ws.append([
            address,
            (coords.get("lat")),
            (coords.get("lng")),
            (z.get("zpid")),
            (z.get("price")),
            (z.get("beds")),
            (z.get("baths")),
            (z.get("livingArea")),
            (z.get("lotSize")),
            (img.get("image_url")),
            (v.get("backyard_status")),
            (v.get("backyard_confidence")),
            (v.get("notes")),
            (lead.get("lead_score")),
        ])

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    return bio.read()


def leads_to_csv_bytes(leads: List[Dict[str, Any]]) -> bytes:
    """Create a CSV file from leads and return raw bytes."""
    output = StringIO()
    
    # Define CSV headers
    headers = [
        "address",
        "lat",
        "lng",
        "zpid",
        "price",
        "beds",
        "baths",
        "livingArea",
        "lotSize",
        "image_url",
        "backyard_status",
        "backyard_confidence",
        "notes",
        "lead_score",
    ]
    
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    
    for lead in leads:
        # Extract nested data
        coords = lead.get("coordinates") or {}
        zillow = lead.get("zillow") or {}
        imagery = lead.get("imagery") or {}
        vision = lead.get("vision") or {}
        
        # Create flattened row
        row = {
            "address": lead.get("address"),
            "lat": coords.get("lat"),
            "lng": coords.get("lng"),
            "zpid": zillow.get("zpid"),
            "price": zillow.get("price"),
            "beds": zillow.get("beds"),
            "baths": zillow.get("baths"),
            "livingArea": zillow.get("livingArea"),
            "lotSize": zillow.get("lotSize"),
            "image_url": imagery.get("image_url"),
            "backyard_status": vision.get("backyard_status"),
            "backyard_confidence": vision.get("backyard_confidence"),
            "notes": vision.get("notes"),
            "lead_score": lead.get("lead_score"),
        }
        writer.writerow(row)
    
    # Convert to bytes
    csv_string = output.getvalue()
    return csv_string.encode('utf-8')


def leads_to_csv_b64(leads: List[Dict[str, Any]], *, filename: str = "leads.csv") -> Dict[str, str]:
    """
    Generates a CSV file from a list of lead objects and returns it as a base64 string.
    """
    csv_bytes = leads_to_csv_bytes(leads)
    payload_b64 = base64.b64encode(csv_bytes).decode("utf-8")
    return {"filename": filename, "base64": payload_b64}