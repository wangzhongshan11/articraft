#!/usr/bin/env python3
"""Generate Simplified Chinese *_c.md for cadquery examples (mecanum_wheel .. yawpitchroll_wrist)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC_DIR = REPO / "sdk" / "_examples" / "cadquery"
RANGE_START = "mecanum_wheel"
RANGE_END = "yawpitchroll_wrist"

_FENCE = re.compile(r"(```[\s\S]*?```)", re.MULTILINE)

# Hand-written translation metadata; expanded to PROSE at import time.
_TAGS = re.compile(r"(tags:\n(?:  - .+\n)+)", re.MULTILINE)


def tags_block(seg0: str) -> str:
    m = _TAGS.search(seg0)
    if not m:
        raise ValueError("no tags block")
    return m.group(1)


def seg0(title: str, description: str, tags: str, heading: str, body: str) -> str:
    return f"---\ntitle: '{title}'\ndescription: '{description}'\n{tags}---\n# {heading}\n\n{body}"


def preserve_tail(en_seg: str, zh_seg: str) -> str:
    """Keep trailing newlines from the English segment (e.g. blank line before a fence)."""
    stripped = en_seg.rstrip("\n")
    suffix = en_seg[len(stripped) :]
    return zh_seg.rstrip("\n") + suffix


# title, description, heading, body (seg0 after heading), optional extra segments after code blocks
T: dict[str, tuple] = {
    "offsetaxis_rotary_stack": (
        "偏轴旋转堆叠",
        "摘自五星偏轴旋转堆叠记录；展示各级旋转模块在空间中侧向错开、仍保持明确串联关系的布局。",
        "偏轴旋转堆叠",
        "与同轴堆叠不同，本五星示例在三维空间中逐段偏移每一级旋转关节，同时仍显式保留级间串联拓扑，便于学习“错轴多转盘”与分层限位配置。",
    ),
    "offsetting_wires_in_2d": (
        "二维线框偏移",
        "二维线框可通过 `Workplane.offset2D()` 进行内外偏移，并在拐角处选用不同的延伸/连接策略。",
        "二维线框偏移",
        "二维线框可通过 `Workplane.offset2D()` 向内或向外偏移；拐角处理可选圆弧（`arc`）或延伸相交（`intersection`）等模式，见第一段示例对比。",
        [
            "\n\n借助 `forConstruction=True`，可把螺栓孔阵列相对零件外轮廓整体内缩——下面在沉头孔示例基础上，将孔位从边缘偏移得到。\n\n",
            "\n\n注意：`Workplane.edges()` 仅用于**选择**对象，不会把选中的边加入建模上下文的 pending 边列表；否则下一次拉伸可能把“仅用于选择”的边一并挤出。若希望这些边参与 `Workplane.offset2D()`，需显式调用 `Workplane.toPending()` 将其加入 pending。\n",
        ],
    ),
    "opposed_twinslide_gripper": (
        "对置双滑台夹爪",
        "摘自五星夹爪记录；展示从共用本体伸出、沿相反棱柱轴滑动的镜像夹爪。",
        "对置双滑台夹爪",
        "该五星夹爪记录是镜像运动学的良好参考：本体承载两只夹爪，行程相等但关节轴方向相反，便于理解对夹与同步开合。",
    ),
    "orthogonal_xy_stage": (
        "正交 XY 工作台",
        "摘自五星精密 XY 工作台记录；展示叠放的 X、Y 滑台及各自导轨组。",
        "正交 XY 工作台",
        "本片段保留五星 XY 工作台记录中的真实拆分：接地底座、带独立导轨的 X 滑架，以及叠在上方的 Y 级。",
    ),
    "panel_with_various_connector_holes": (
        "多种连接器开孔的面板",
        "在薄板上阵列加工 DB9、D-sub、安装孔等多种连接器开口的 CadQuery 示例。",
        "多种连接器开孔的面板",
        "在参数化薄板上循环布置多种连接器轮廓（圆孔、D 形口、安装孔阵列等），适合面板/机箱开孔类建模。",
    ),
    "parametric_pin_header": (
        "参数化排针",
        "由塑料基座与重复镀金针脚组成的直插排针装配体。",
        "参数化排针",
        "本示例对应 `cq-electronics` 直插排针模型：可配置行/列数、针长、倒角与基座挖孔。",
    ),
    "pitray_clip": (
        "PiTray 卡扣支架",
        "钣金式支架装配：直角托盘支架与 DIN 导轨卡扣组合。",
        "PiTray 卡扣支架",
        "本示例对应 `cq-electronics` PiTray 卡扣装配模型。",
    ),
    "plate_with_hole": (
        "带孔板",
        "矩形盒体并在顶面中心加工通孔的基础示例。",
        "带孔板",
        "最简盒体加中心孔。\n\n`\">Z\"` 选择结果盒体的最顶面；孔默认落在工作平面原点投影处——上一工作平面原点在 (0,0,0) 时，投影即面中心。默认孔深为贯穿整件。\n",
    ),
    "polygons": (
        "多边形孔",
        "可在堆栈各点生成多边形轮廓；适用于固件不做小孔补偿的 3D 打印机等场景。",
        "多边形孔",
        "可在堆栈各点生成多边形轮廓；适用于固件不做小孔圆度补偿的 3D 打印机等场景。",
    ),
    "polylines": (
        "折线",
        "`Workplane.polyline()` 可用大量首尾相连的直线段定义轮廓。",
        "折线",
        "`Workplane.polyline()` 可用大量首尾相连的直线段定义轮廓。\n\n本例用折线画出工字梁截面的一半，再 `mirrorY()` 得到完整截面并拉伸。\n",
    ),
    "portal_gantry_with_vertical_slide": (
        "门型龙门与垂直滑台",
        "摘自五星门型龙门记录；展示横梁滑车与下挂 Z 向滑台。",
        "门型龙门与垂直滑台",
        "本片段保留五星龙门记录的三段真实拆分：刚性门型框架、横梁滑车、独立下挂垂直滑台。",
    ),
    "prismaticrevolute_chain": (
        "移动副-转动副链",
        "摘自五星检测夹具记录；展示滑台承载铰接翻板的 PR 拓扑。",
        "移动副-转动副链",
        "五星检测夹具记录适合作为该拓扑模板：基座导向运动与远端翻板转动分离清晰。",
    ),
    "prismaticrevoluterevolute_chain": (
        "移动副-转动副-转动副链",
        "摘自五星直线双旋转模块记录；展示滑台 feeding 肩部和前臂的两级转动。",
        "移动副-转动副-转动副链",
        "对应五星直线双旋转模块的真实混合拓扑：先平移，再在移动滑架上连续两次转动。",
    ),
    "rack_and_pinion": (
        "齿条与齿轮",
        "齿条与直齿轮啮合，并保留 `Workplane.gear()` 插件式工作流。",
        "齿条与齿轮",
        "齿条可直接构建；从动小齿轮仍可使用内嵌的 `Workplane.gear()` 辅助，工作流与上游 `cq_gears` 一致。",
    ),
    "raspberry_pi_3_model_b_assembly": (
        "树莓派 3 Model B 装配",
        "带约束的 PCB 装配：板体、阻焊层、排针、RJ45 与 BGA 封装。",
        "树莓派 3 Model B 装配",
        "本示例对应 `cq-electronics` 树莓派 3 Model B 装配模型。",
    ),
    "reinforcing_a_junction_with_a_fillet": (
        "用圆角加强连接",
        "在选定边上施加圆角，以加强两特征之间的连接。",
        "用圆角加强连接",
        "",
    ),
    "remote_enclosure": (
        "遥控器外壳",
        "紧凑外壳：抽壳顶盖、沉头按键孔与配合盖。",
        "遥控器外壳",
        "",
    ),
    "resin_mold": (
        "树脂模具",
        "简易树脂浇注模：线槽腔、安装孔与注料孔。",
        "树脂模具",
        "",
    ),
    "revoluteprismatic_chain": (
        "转动副-移动副链",
        "摘自五星检测臂记录；展示转台铰链驱动直线伸缩级。",
        "转动副-移动副链",
        "摘自五星检测臂记录的裁剪片段：保留真实 RP 混合拓扑及滑台上的检测头细节。",
    ),
    "revoluteprismaticrevolute_chain": (
        "转动副-移动副-转动副链",
        "摘自五星服务机械臂记录；展示回转底座、中段滑台与腕部俯仰。",
        "转动副-移动副-转动副链",
        "保留五星服务机械臂记录的三级真实运动堆叠；省略辅助形体，但零件布局与关节原点一致。",
    ),
    "ring_gears_and_planetary_gearsets": (
        "内齿圈与行星轮系",
        "使用内嵌 `sdk` 齿轮 API 构建内齿圈与行星轮系。",
        "内齿圈与行星轮系",
        "内齿圈类与行星轮辅助函数已直接移植到 `sdk`，可组合固定内齿圈与完整轮系，无需依赖上游包。",
    ),
    "rj45_surface_mount_jack": (
        "RJ45 贴片插座",
        "单口 RJ45 模块化插座：开口、键槽与卡扣限位细节。",
        "RJ45 贴片插座",
        "本示例对应 `cq-electronics` 单口贴片 RJ45 插座模型。",
    ),
    "rotary_base_with_vertical_slide": (
        "旋转底座与垂直滑台",
        "摘自五星旋转升降模块记录；展示偏航底座上的垂直棱柱级。",
        "旋转底座与垂直滑台",
        "保留五星旋转升降记录的双轴机床模块布局：一级转动底座 + 其上的垂直移动副。",
    ),
    "rotated_workplanes": (
        "旋转工作平面",
        "相对另一工作平面指定旋转角，可创建旋转后的草图平面。",
        "旋转工作平面",
        "相对另一工作平面指定旋转角即可创建旋转工作平面。本变体以米为单位直接编写尺寸。",
    ),
    "rounding_corners_with_fillet": (
        "用圆角倒圆角",
        "选择实体边并调用圆角函数完成倒角。",
        "用圆角倒圆角",
        "对实体边执行圆角：先选边，再 `fillet()`。\n\n下面对简单板的全部边做圆角。\n",
    ),
    "shelling_to_create_thin_features": (
        "抽壳生成薄壁特征",
        "抽壳将实心体变为等厚度薄壳。",
        "抽壳生成薄壁特征",
        "抽壳将实心体变为等厚度薄壳。\n\n要对零件“挖空”内腔，向 `Workplane.shell()` 传入**负**厚度。\n",
        [
            "\n\n**正**厚度会在外侧包裹一层带圆角的壳体，原实体成为被掏空部分。\n\n",
            "\n\n可用面选择器指定要从空心结果中移除的面。\n\n",
            "\n\n也可用更复杂的选择器一次移除多个面。\n\n",
        ],
    ),
    "simple_rectangular_plate": (
        "简单矩形板",
        "几乎最简单的示例：矩形盒体。",
        "简单矩形板",
        "几乎最简单的 CadQuery 入门示例：拉伸一个矩形盒体。",
    ),
    "single_continuous_rotary_shaft": (
        "单连续旋转轴",
        "摘自五星陶轮记录；展示连续主轴与固定刀盘。",
        "单连续旋转轴",
        "保留五星陶轮记录的三段拆分：接地底座、连续主轴、由主轴承载的固定刀盘。",
    ),
    "single_pitch_axis_module": (
        "单俯仰轴模块",
        "摘自五星电动倾转支架记录；展示支架、摇篮与居中俯仰轴。",
        "单俯仰轴模块",
        "保留五星倾转记录的真实支架-摇篮拆分；省略辅助网格构造，俯仰关节位置一致。",
    ),
    "single_prismatic_slider": (
        "单棱柱滑台",
        "摘自五星机床直线轴记录；展示导轨、滑车、刮板与行程限位。",
        "单棱柱滑台",
        "五星直线轴记录的核心 `build_object_model()` 片段：保留真实滑车细节，而非简化为方盒。",
    ),
    "single_revolute_hinge": (
        "单转动铰链",
        "摘自五星壁挂柜记录；展示柜体、门扇与铰链布局。",
        "单转动铰链",
        "保留五星橱柜示例的真实零件拆分与铰链位置；此处省略辅助网格与尺寸常量，对象逻辑不变。\n\n关键符号约定：关门时门扇沿铰链线局部 `+X` 伸出，故 `axis=(0, 0, 1)` 使关节角增大时自由边摆向局部/前方 `+Y`，而非撞入柜体。\n",
    ),
    "single_roll_axis_module": (
        "单滚转轴模块",
        "摘自五星电动滚转台记录；展示框架底座、传感管与同轴滚转关节。",
        "单滚转轴模块",
        "五星滚转示例不仅是两板之间的圆柱：还包含真实框架、电机壳体与绕滚转轴布置的传感管组件。",
    ),
    "single_yaw_axis_module": (
        "单偏航轴模块",
        "摘自五星云台记录；展示底座、转盘、载荷立柱与固定安装位。",
        "单偏航轴模块",
        "五星云台示例比“裸转 puck”更丰富：转动副转盘 + 固定立柱，将载荷抬升至轴上方。",
    ),
    "splitting_an_object": (
        "分割实体",
        "可用工作平面分割对象，并保留一侧或两侧结果。",
        "分割实体",
        "可用工作平面分割对象，并保留一侧或两侧半体。",
    ),
    "spur_helical_herringbone_gears": (
        "直齿、斜齿与人字齿轮",
        "使用内嵌齿轮类，并保留 `cadquery.Workplane.gear()` 插件工作流。",
        "直齿、斜齿与人字齿轮",
        "示例使用内嵌 `sdk` 齿轮类，同时在 `cadquery.Workplane` 上保持熟悉的 `cq_gears` 插件模式。下列参数以米编写，导出网格已符合基础 SDK 坐标/单位约定。",
    ),
    "tagging_objects": (
        "对象标记",
        "`Workplane.tag()` 可为链中某一对象打上字符串标记，以便后续步骤引用。",
        "对象标记",
        "`Workplane.tag()` 可为链中某一对象打上字符串标记，以便后续步骤引用。\n\n`Workplane.workplaneFromTagged()` 对标记对象应用 `Workplane.copyWorkplane()`。例如从同一面挤出两个不同实体后，再用普通选择器找回原面会变得困难。\n",
        [
            "\n\n标记还可与多数选择器联用，包括 `Workplane.vertices()`、`Workplane.faces()`、`Workplane.edges()`、`Workplane.wires()`、`Workplane.shells()`、`Workplane.solids()` 与 `Workplane.compounds()`。\n\n",
        ],
    ),
    "the_classic_occ_bottle": (
        "经典 OCC 瓶子",
        "CadQuery 基于 OpenCascade.org (OCC) 内核；熟悉 OCC 的开发者都了解著名的“瓶子”示例。",
        "经典 OCC 瓶子",
        "CadQuery 基于 OpenCascade.org (OCC) 建模内核；熟悉 OCC 的开发者都了解著名的“瓶子”示例。\n\n与 OCC 官方版本相比，本示例仍算较长（约 13 行），但比 pythonOCC 版本短一个数量级。\n",
    ),
    "thread": (
        "螺纹",
        "由参数化螺旋与直纹面构造螺纹形体。",
        "螺纹",
        "",
    ),
    "threejoint_revolute_chain": (
        "三关节转动链",
        "摘自五星麦克风悬臂记录；展示底座偏航、肘部俯仰与腕部俯仰的 3R 链。",
        "三关节转动链",
        "五星麦克风悬臂是真实 3R 链的良好参考：底座、下臂、上臂与末端工具各司其职。",
    ),
    "threestage_telescoping_slide": (
        "三级伸缩滑台",
        "摘自五星三级滑台记录；展示嵌套导轨、端部支架与限位特征。",
        "三级伸缩滑台",
        "相较两级版本，五星三级滑台记录增加显式限位，并区分外/中/内三层导轨实体。",
    ),
    "twojoint_revolute_chain": (
        "双关节转动链",
        "摘自五星阅读灯记录；展示底座、下臂与上组件的真实 2R 链。",
        "双关节转动链",
        "保留五星阅读灯记录的真实分解，而非匿名方块链。\n\n两段臂杆均沿各自铰链局部 `+X` 伸出，故俯仰关节使用 `axis=(0, -1, 0)`，使关节角增大时臂杆向上抬起。\n",
    ),
    "twostage_telescoping_slide": (
        "两级伸缩滑台",
        "摘自五星两级滑台记录；展示固定底板与嵌套外/中/内导轨。",
        "两级伸缩滑台",
        "五星滑台记录是嵌套直线级的良好范式：每级导轨为独立零件并带行程限位。\n\n对任意嵌套直线级，运动件在**全行程**仍应保持插入套筒内。按伸展姿态确定各级长度，再设置行程上限，使滑台在完全脱出前停止。\n",
        [
            "\n\n与之配套的“保持插入”测试模式如下：\n\n",
        ],
    ),
    "using_construction_geometry": (
        "构造几何",
        "可绘制仅用于定位的特征：用其顶点确定其他特征位置；不直接参与成形的几何称为 `Construction Geometry`。",
        "构造几何",
        "可绘制仅用于定位的特征：用其顶点确定其他特征位置；不直接参与成形的几何称为 `Construction Geometry`。\n\n下例先画矩形，再用其顶点定位一组孔。\n",
    ),
    "using_point_lists": (
        "点列表",
        "需在多处创建特征而反复 `Workplane.center()` 过于繁琐时，可用点列表。",
        "点列表",
        "需在多处创建特征而反复 `Workplane.center()` 过于繁琐时，可用点列表。\n\n将点列表压入堆栈后，多数构造方法（如 `Workplane.circle()`、`Workplane.rect()`）会对堆栈上所有点同时操作。\n",
    ),
    "vane_array_with_independent_pivots": (
        "独立枢轴叶片阵列",
        "摘自五星叶片阵列记录；展示刚性框架上多个独立叶片零件。",
        "独立枢轴叶片阵列",
        "五星叶片阵列示例展示如何在单一接地框架上编写重复、彼此独立的转动关节。",
    ),
    "vertical_slide_with_wrist_hinge": (
        "垂直滑台与腕部铰链",
        "摘自五星 Z 轴腕部模块记录；展示升降滑车与铰接鼻座。",
        "垂直滑台与腕部铰链",
        "保留五星 Z 轴腕部记录的立柱、滑车与腕部拆分；适合升降+俯仰工具头范式。",
    ),
    "wall_vent_with_louvered_grille": (
        "百叶格栅墙式通风口",
        "摘自墙式通风工作台记录；CadQuery 编写的通风壳体、真实栅条与内凹风道。",
        "百叶格栅墙式通风口",
        "当通风口/格栅需呈现为可制造的整洁外壳而非程序网格碎片堆叠时，本裁剪 CadQuery 示例很有参考价值。",
    ),
    "worm_gear": (
        "蜗杆",
        "使用内嵌 `sdk` 齿轮实现生成蜗杆实体。",
        "蜗杆",
        "蜗杆移植保持与上游相同的紧凑构造参数形式，返回标准 CadQuery 实体，可在统一 SDK 中复用。",
    ),
    "xyz_cartesian_stage": (
        "XYZ 笛卡尔工作台",
        "摘自五星 XYZ 工作台记录；展示叠放的 X/Y/Z 滑台及辅助盒体几何。",
        "XYZ 笛卡尔工作台",
        "五星 XYZ 工作台是紧凑且可信的三轴叠放参考，无需厚重网格导出层。",
    ),
    "yawpitchroll_wrist": (
        "偏航-俯仰-滚转腕部",
        "摘自五星工具腕记录；展示嵌套的偏航、俯仰与滚转关节。",
        "偏航-俯仰-滚转腕部",
        "保留五星腕部记录的真实嵌套轴布局：基座壳体、偏航环、俯仰叉与独立滚转主轴。",
    ),
}


def prose_segments(text: str) -> list[str]:
    return [p for p in _FENCE.split(text) if not (p.startswith("```") and p.endswith("```"))]


def apply_prose(text: str, translations: list[str]) -> str:
    parts = _FENCE.split(text)
    pi = 0
    out: list[str] = []
    for part in parts:
        if part.startswith("```") and part.endswith("```"):
            out.append(part)
        else:
            if pi >= len(translations):
                raise ValueError(f"too few prose segments: need index {pi}, have {len(translations)}")
            out.append(translations[pi])
            pi += 1
    if pi != len(translations):
        raise ValueError(f"too many prose translations: expected {pi}, got {len(translations)}")
    return "".join(out)


def build_prose() -> dict[str, list[str]]:
    prose: dict[str, list[str]] = {}
    for stem, spec in T.items():
        en = prose_segments((SRC_DIR / f"{stem}.md").read_text(encoding="utf-8"))
        tags = tags_block(en[0])
        if len(spec) == 4:
            title, desc, heading, body = spec
            extra: list[str] = []
        else:
            title, desc, heading, body, extra = spec[0], spec[1], spec[2], spec[3], list(spec[4])
        zh: list[str] = [preserve_tail(en[0], seg0(title, desc, tags, heading, body))]
        for i, seg in enumerate(en[1:]):
            if i < len(extra):
                zh.append(preserve_tail(seg, extra[i]))
            else:
                zh.append(seg)
        if len(zh) != len(en):
            raise ValueError(f"{stem}: built {len(zh)} vs en {len(en)}")
        prose[stem] = zh
    return prose


PROSE: dict[str, list[str]] = build_prose()


def sources_in_range() -> list[Path]:
    sources = sorted(p for p in SRC_DIR.glob("*.md") if not p.stem.endswith("_c"))
    return [p for p in sources if RANGE_START <= p.stem <= RANGE_END]


def write_c(stem: str) -> None:
    src = SRC_DIR / f"{stem}.md"
    raw = src.read_text(encoding="utf-8")
    if stem not in PROSE:
        raise KeyError(f"missing PROSE translations for {stem}")
    en_prose = prose_segments(raw)
    zh_prose = PROSE[stem]
    if len(en_prose) != len(zh_prose):
        raise ValueError(
            f"{stem}: prose segment count mismatch (en={len(en_prose)}, zh={len(zh_prose)})"
        )
    out = apply_prose(raw, zh_prose)
    tgt = SRC_DIR / f"{stem}_c.md"
    tgt.write_text(out, encoding="utf-8", newline="\n")
    print(f"wrote {tgt.name}")


def main() -> int:
    sources = sources_in_range()
    expected = len(sources)
    created: list[str] = []
    for src in sources:
        stem = src.stem
        tgt = SRC_DIR / f"{stem}_c.md"
        if stem not in PROSE:
            print(f"skip (no PROSE): {stem}", file=sys.stderr)
            continue
        write_c(stem)
        created.append(f"{stem}_c.md")

    c_files = sorted(
        p.name
        for p in SRC_DIR.glob("*_c.md")
        if RANGE_START <= p.stem.removesuffix("_c") <= RANGE_END
    )
    print(f"\n*_c.md in range: {len(c_files)} (expected {expected})")
    if len(c_files) != expected:
        print("ERROR: count mismatch", file=sys.stderr)
        return 1
    if created:
        print("\nCreated:")
        for name in sorted(created):
            print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
