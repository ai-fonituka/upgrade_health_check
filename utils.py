from lxml import etree
from collections import defaultdict

FIELDS_TO_COMPARE = ["filter_condition", "condition", "active", "script", "template", "when", "order"]

FRIENDLY_CLASS_NAMES = {
    "sys_script": "Business Rule",
    "sys_script_include": "Script Include",
    "sys_ui_action": "UI Action",
    "sys_dictionary": "Dictionary Entry",
    "sys_ui_policy": "UI Policy",
    "sys_data_policy": "Data Policy",
    "sys_email_template": "Email Template",
    "sys_notification": "Notification",
    "sys_transform_map": "Transform Map",
    "sys_flow": "Flow Designer Flow",
    "sys_choice": "Choice List",
    "sys_update_set": "Update Set",
    "sys_security_acl": "Access Control (ACL)",
    "sysauto_script": "Scheduled Job",
    "sys_properties": "System Property",
    "sysevent_email_action": "Email Notification",
    "sys_report": "Report",
    "sys_ui_form_section": "Form Section",
    "sys_ui_form": "Form Layout",
    "sys_relationship": "Table Relationship",
    "sys_app": "Application",
    "sys_app_module": "Application Module",
    "sys_role": "Role",
    "sys_user_role": "User Role",
    "sys_script_fix": "Fix Script"
}

def get_friendly_class_name(class_name):
    return FRIENDLY_CLASS_NAMES.get(class_name, class_name)

def extract_base_records(tree):
    records = {}
    for node in tree.findall(".//sys_update_xml"):
        key = node.findtext("name")
        payload = node.findtext("payload")
        if payload and key:
            try:
                inner_xml = etree.fromstring(payload.strip().encode("utf-8"))
                record_update = inner_xml if inner_xml.tag == "record_update" else inner_xml.find("record_update")
                if record_update is not None:
                    for child in record_update:
                        if not isinstance(child.tag, str):
                            continue
                        if not child.tag.startswith("sys_"):
                            continue
                        found_field = any(child.find(field) is not None for field in FIELDS_TO_COMPARE)
                        if not found_field:
                            continue
                        fields = {field: child.findtext(field) or "" for field in FIELDS_TO_COMPARE}
                        name = child.findtext("name") or child.findtext("sys_name")
                        class_name = child.tag
                        records[key.strip().lower()] = {"name": name, "fields": fields, "class": class_name}
                        break
            except Exception as e:
                print(f"⚠️ Erro ao processar payload em {key}: {e}")
    return records

def extract_custom_records(tree):
    records = {}
    for node in tree.getroot():
        if not isinstance(node.tag, str):
            continue
        sys_id = (node.findtext("sys_id") or "").strip()
        class_name = (node.findtext("sys_class_name") or node.tag).strip()
        name = node.findtext("name") or node.findtext("sys_name")
        fields = {field: node.findtext(field) or "" for field in FIELDS_TO_COMPARE}
        if sys_id and class_name:
            key = f"{class_name}_{sys_id}".strip().lower()
            records[key] = {"name": name, "fields": fields, "class": class_name}
    return records

def group_by_class(records_dict):
    grouped = defaultdict(list)
    for key, record in records_dict.items():
        record_with_key = {**record, "key": key}
        grouped[record["class"]].append(record_with_key)
    return grouped
