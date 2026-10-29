# 配色方案总表

由 `scripts/sync_refs.py` 从 `palette.py` 生成，改配色请改 `palette.py` 后重新生成。

- 全部方案对所有图型通用；不指定方案时用 `macaron`。一篇文档或一批图只用一套。
- 四槽语义：槽0 处理 / 任务 / 类 / 组件，槽1 起止 / 接口 / 库，槽2 文档 / 数据 / 枚举 / 制品，槽3 判断 / 网关 / 参与者 / 约束。
- 主色独立于四个槽，只给"一张图里只有一处"的强调角色（关键路径、核心实体、中心主题、本次改动）。
- 派生规则：浅填充的描边 = 填充加深 30%，字色 = 同色相加深到 4.5:1；深填充描边同填充、白字；soft 容器 = 描边色对底 90% 浅调；连线对底 ≥3:1；系列色 = 槽填充 + 方案附加色，不含主色。
- 系列色用于数据图、思维导图分支、泳道 / 分组轮换；状态色（成功 / 警告 / 失败 / 信息 / 完成）所有方案共用。

状态色：ok `#4AB777`、warn `#E8A35D`、bad `#E35144`、info `#516DF6`、done `#BBBBBB`

| 方案 | 名称 | 气质 | 底 / 正文 / 连线 | 主色 | 槽0–3 填充 | 系列色 |
|---|---|---|---|---|---|---|
| ★ `macaron` | 马卡龙 | 薰衣草 / 蜜桃 / 薄荷 / 杏，宝蓝强调；通用默认 | `#FFFFFF` `#33384A` `#3B6FC2` | `#3B6FC2` | `#D2D6F1` `#FBDBD1` `#D8F0ED` `#F6DEB6` | `#D2D6F1` `#FBDBD1` `#D8F0ED` `#F6DEB6` `#DEE7CD` `#A4A7BC` |
| `cotton` | 棉糖 | 粉蓝 / 粉红 / 粉绿 / 鹅黄，灰线，钢蓝强调 | `#FFFFFF` `#333333` `#909090` | `#1B6EBB` | `#C8E2FA` `#EDD2D6` `#DDEFD9` `#F0DA9D` | `#C8E2FA` `#EDD2D6` `#DDEFD9` `#F0DA9D` `#9CB0C3` `#B9A4A7` |
| `mist` | 薄雾 | 淡蓝 / 淡绿 / 杏 / 淡紫，灰绿字，青蓝强调 | `#FFFFFF` `#3A4A40` `#919590` | `#248AB2` | `#CEEAF5` `#CEE0CA` `#FCE8D0` `#E3D7EC` | `#CEEAF5` `#CEE0CA` `#FCE8D0` `#E3D7EC` `#A1B7BF` `#A1AF9E` |
| `morandi` | 莫兰迪 | 灰绿 / 杏 / 淡紫 / 淡青，橄榄强调 | `#FFFFFF` `#3E4A3D` `#8C8D83` | `#5E7A55` | `#E4F5DA` `#F7D4B5` `#D2D6F8` `#DBF5F5` | `#E4F5DA` `#F7D4B5` `#D2D6F8` `#DBF5F5` `#F9DCDB` `#B9E9E7` |
| `cream` | 奶油 | 奶油 / 卡其 / 淡绿 / 米灰，橄榄棕强调 | `#FFFFFE` `#5A4E3A` `#999382` | `#8C7A55` | `#FDEED4` `#E0D3BA` `#DAE9D9` `#C4BCA6` | `#FDEED4` `#E0D3BA` `#DAE9D9` `#C4BCA6` `#C5BAA5` `#AFA591` |
| `pebble` | 鹅卵石 | 蓝灰 / 藕粉 / 浅灰，石墨强调，冷灰底 | `#F9FBFC` `#3C454B` `#8B9297` | `#5F6C72` | `#BCCBCF` `#DDC1CE` `#DCE0E3` `#8B9297` | `#BCCBCF` `#DDC1CE` `#DCE0E3` `#8B9297` `#939EA1` `#AC97A1` |
| `sage` | 鼠尾草 | 鼠尾草绿四阶，大地色系列，白底 | `#FFFFFF` `#30473D` `#3D4D46` | `#38755B` | `#6B9080` `#A4C3B2` `#CCE3DE` `#F6FFF8` | `#6B9080` `#A4C3B2` `#CCE3DE` `#748EAF` `#AFA57B` `#C19D5F` `#A87365` `#9B8867` |
| `candy` | 糖果 | 薰衣草 / 长春花 / 青 / 粉红，靛蓝强调 | `#FAFAFA` `#2E2F45` `#8388BC` | `#202DB6` | `#C7CBF5` `#7B87EC` `#BAEAEB` `#F4BEDB` | `#C7CBF5` `#7B87EC` `#BAEAEB` `#F4BEDB` `#B0E28F` `#9B9EBF` |
| `slate` | 石板珊瑚 | 石板蓝 + 珊瑚红，暖白底 | `#FFFEFC` `#2A3346` `#8B929E` | `#3D4B67` | `#E7EAF0` `#C9CCD2` `#FBE2E3` `#EB6E72` | `#E7EAF0` `#C9CCD2` `#FBE2E3` `#EB6E72` `#B4B7BB` `#9D9FA4` |
| `moss` | 苔藓 | 苔绿 / 灰绿 / 奶黄，深苔强调，暖白底 | `#FCFCF8` `#1F3C23` `#8B9288` | `#1F3C23` | `#E7EEE0` `#BEC6BC` `#D0D9C8` `#FFF4CF` | `#E7EEE0` `#BEC6BC` `#D0D9C8` `#828B7E` `#B4BAAF` `#949A93` |
| `latte` | 拿铁 | 杏黄 / 薄荷 / 琥珀，炭灰强调 | `#FEFEFE` `#3B3D4B` `#8C8F91` | `#3B3D4B` | `#FBE2B4` `#C7C8CC` `#C5E0DA` `#F4B246` | `#FBE2B4` `#C7C8CC` `#C5E0DA` `#F4B246` `#E6BCBD` `#F5EBDF` |
| `blush` | 胭脂 | 粉 / 珊瑚 / 米粉，灰紫强调，暖粉底 | `#FFF7F5` `#5A5A70` `#AC7D78` | `#7D7D98` | `#F6DAD7` `#F37464` `#FBE9E6` `#F9B6AE` | `#F6DAD7` `#F37464` `#FBE9E6` `#F9B6AE` `#C0AAA8` `#BE5A4E` |

完整 token（含描边、字色、便签色、渐层）：`python $SKILL/scripts/palette.py show <方案>`
