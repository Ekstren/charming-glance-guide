from pathlib import Path

INDEX=Path('index.html')
V1=Path('scripts/patch_t4_class_order_dominator_roles_v1.py')
OLD="['Conqueror','Guardian','Destroyer','Dominator']"
NEW="['Destroyer','Dominator','Conqueror','Guardian']"

index=INDEX.read_text(encoding='utf-8')
index=index.replace(f"const S2_BUILD_CLASSES={OLD};",f"const S2_BUILD_CLASSES={NEW};")
index=index.replace(f"const S2_BUILD_CLASSES_LIVE={OLD};",f"const S2_BUILD_CLASSES_LIVE={NEW};")
index=index.replace(f"const S2_CLASSES={OLD};",f"const S2_CLASSES={NEW};")
for token in (
    f"const S2_BUILD_CLASSES={NEW};",
    f"const S2_BUILD_CLASSES_LIVE={NEW};",
    f"const S2_CLASSES={NEW};",
):
    if token not in index: raise RuntimeError(f'missing normalized class order: {token}')
INDEX.write_text(index,encoding='utf-8')

# Teach the main class/order audit patch about the later seasonal renderer override too.
v1=V1.read_text(encoding='utf-8')
anchor="index=index.replace(f\"const S2_BUILD_CLASSES={ORDER_OLD};\",f\"const S2_BUILD_CLASSES={ORDER_NEW};\")\n"
line="index=index.replace(f\"const S2_BUILD_CLASSES_LIVE={ORDER_OLD};\",f\"const S2_BUILD_CLASSES_LIVE={ORDER_NEW};\")\n"
if line not in v1:
    if anchor not in v1: raise RuntimeError('main class-order patch anchor missing')
    v1=v1.replace(anchor,anchor+line,1)
check="if f\"const S2_BUILD_CLASSES={ORDER_NEW};\" not in index:raise RuntimeError('Build class order did not land')\n"
checkline="if f\"const S2_BUILD_CLASSES_LIVE={ORDER_NEW};\" not in index:raise RuntimeError('Live build class order did not land')\n"
if checkline not in v1:
    if check not in v1: raise RuntimeError('main class-order verification anchor missing')
    v1=v1.replace(check,check+checkline,1)
V1.write_text(v1,encoding='utf-8')
print('Normalized live T4 class order to Destroyer, Dominator, Conqueror, Guardian')
