# logic.py
from utils import extract_base_records, extract_custom_records, group_by_class, get_friendly_class_name
from ai_summary import summarize_changes
from export import export_csv, export_docx, export_pdf, export_html
import streamlit as st
import difflib
import streamlit.components.v1 as components
import pandas as pd
from html import escape

FIELDS_TO_COMPARE = ["filter_condition", "condition", "active", "script", "template", "when", "order"]

def process_comparison(base_tree, custom_tree):
    base_records = extract_base_records(base_tree)
    custom_records = extract_custom_records(custom_tree)

    new_records = {}
    modified_records = {}
    unchanged_records = {}

    for key, record in custom_records.items():
        if key not in base_records:
            new_records[key] = record
        else:
            diffs = {}
            base_fields = base_records[key]["fields"]
            custom_fields = record["fields"]
            for field in FIELDS_TO_COMPARE:
                if base_fields[field].strip() != custom_fields[field].strip():
                    diffs[field] = {"before": base_fields[field], "after": custom_fields[field]}
            if diffs:
                modified_records[key] = {
                    "name": record["name"],
                    "differences": diffs,
                    "class": record["class"]
                }
            else:
                unchanged_records[key] = record

    st.subheader("📌 Results")
    st.markdown(f"**New records:** {len(new_records)}")
    st.markdown(f"**Modified records:** {len(modified_records)}")
    st.markdown(f"**Unchanged records:** {len(unchanged_records)}")

    results = []
    new_by_class = group_by_class(new_records)
    modified_by_class = group_by_class(modified_records)

    with st.expander("🆕 New Records" if new_records else ""):
        for class_name, records in new_by_class.items():
            friendly_name = get_friendly_class_name(class_name)
            st.markdown(f"## 🧩 {friendly_name} ({len(records)})")
            for record in records:
                key = record["key"]
                title = f"{record['name']} ({key})"
                st.markdown(f"### 🟢 {title}")
                for field, value in record["fields"].items():
                    st.markdown(f"**{field}**: \n```\n{value}\n```")
                with st.spinner("Generating summary with AI..."):
                    summary = summarize_changes(title, {f: {"before": "", "after": v} for f, v in record["fields"].items() if v.strip()})
                st.success("Summary generated:")
                st.markdown(summary)
                results.append({"name": title, "type": "new", "summary": summary, "class": class_name, "before": "", "after": str(record["fields"])})

    with st.expander("✏️ Modified Records" if modified_records else ""):
        for class_name, records in modified_by_class.items():
            friendly_name = get_friendly_class_name(class_name)
            st.markdown(f"## 🧩 {friendly_name} ({len(records)})")
            for record in records:
                key = record["key"]
                title = f"{record['name']} ({key})"
                st.markdown(f"### ✏️ {title}")
                for field, values in record["differences"].items():
                    st.markdown(f"#### Field: {field}")
                    before_lines = values["before"].splitlines()
                    after_lines = values["after"].splitlines()
                    matcher = difflib.SequenceMatcher(None, before_lines, after_lines)
                    html = "<pre style='font-family: monospace;'>"
                    context = 5
                    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                        if tag == "equal":
                            if i2 - i1 <= context * 2:
                                for offset, line in enumerate(before_lines[i1:i2]):
                                    html += f"<span style='color:#888;'>  {i1 + offset + 1:>4}: {escape(line)}</span><br>"
                            else:
                                html += "<span style='color:#aaa;'>  ...</span><br>"
                        elif tag == "replace":
                            start = max(i1 - context, 0)
                            end = min(i2 + context, len(before_lines))
                            for offset, line in enumerate(before_lines[start:i1]):
                                html += f"<span style='color:#888;'>  {start + offset + 1:>4}: {escape(line)}</span><br>"
                            for offset, line in enumerate(before_lines[i1:i2]):
                                html += f"<span style='background-color:#fddede;'>- {i1 + offset + 1:>4}: {escape(line)}</span><br>"
                            for offset, line in enumerate(after_lines[j1:j2]):
                                html += f"<span style='background-color:#d4fcdc;'>+ {j1 + offset + 1:>4}: {escape(line)}</span><br>"
                            for offset, line in enumerate(after_lines[j2:j2+context]):
                                if j2 + offset < len(after_lines):
                                    html += f"<span style='color:#888;'>  {j2 + offset + 1:>4}: {escape(line)}</span><br>"
                        elif tag == "delete":
                            for offset, line in enumerate(before_lines[i1:i2]):
                                html += f"<span style='background-color:#fddede;'>- {i1 + offset + 1:>4}: {escape(line)}</span><br>"
                        elif tag == "insert":
                            for offset, line in enumerate(after_lines[j1:j2]):
                                html += f"<span style='background-color:#d4fcdc;'>+ {j1 + offset + 1:>4}: {escape(line)}</span><br>"
                    html += "</pre>"
                    components.html(html, height=300, scrolling=True)
                with st.spinner("Generating summary with AI..."):
                    summary = summarize_changes(title, record["differences"])
                st.success("Summary generated:")
                st.markdown(summary)
                results.append({"name": title, "type": "modified", "summary": summary, "class": class_name, "before": str(values["before"]), "after": str(values["after"])})

    # Export buttons
    if results:
        export_csv(results)
        export_docx(results)
        export_pdf(results)
        export_html(results)
