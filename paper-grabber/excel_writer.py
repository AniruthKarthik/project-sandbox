import os
import openpyxl

EXCEL_PATH = os.path.expanduser("~/Documents/papers/research_papers.xlsx")

def save_to_excel(data):
    if not os.path.exists(EXCEL_PATH):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Title", "Authors", "Abstract", "Year", "Citations", "EID", "Link"])
    else:
        wb = openpyxl.load_workbook(EXCEL_PATH)
        ws = wb.active

    for row in ws.iter_rows(values_only=True):
        if row[5] == data["eid"]:
            print("⚠️ Duplicate found. Skipping.")
            return

    ws.append([
        data["year"],
        data["citations"],
        data["title"],
        ", ".join(data["authors"]),
        data["abstract"],
        data["eid"],
        data["url"]
    ])
    wb.save(EXCEL_PATH)
    print("✅ Saved to Excel")

