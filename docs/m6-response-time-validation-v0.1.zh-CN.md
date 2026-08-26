# M6 5 ms 响应与最小遮挡实测方案

状态：`商家响应时间语义已确认，最小输入脉宽/最小遮挡时间待实测`。

本文件把商家关于“5 ms”的回复转换成可验收的测试，不把响应时间误写成最小检测门槛。

## 1. 当前可用结论

商家对用户问题的回复是：“被测信号发生变化，到传感器输出信号真正跟着变化完成，中间需要 5 ms；不要求物体必须持续遮挡 5 ms 才能检测。”因此当前记录为：

- `5 ms`：输入状态变化到 NPN 输出完成变化的响应时间语义；
- 不是：物体必须连续遮挡 5 ms 才开始检测；
- 尚未证明：遮挡小于 5 ms 时一定会产生有效输出脉冲；
- 尚未确认：上升沿/下降沿分别的最大值、内部滤波、最小输入脉宽、最小输出脉宽和重复检测率。

如果遮挡在传感器输出完成变化前已经结束，传感器可能没有输出可捕获的稳定状态。ESP32 中断、硬件锁存或软件缓存只能保存已经产生的脉冲，不能修复传感器本身漏检。

## 2. 乒乓球遮挡时间的估算

先用简单上界估算，不把它当作实测：

```text
t_block ≈ L_effective / v_perpendicular
```

其中 `L_effective` 是球体沿光束运动方向实际遮挡的弦长，通常小于等于球径；`v_perpendicular` 是球速在穿过光束方向上的分量。若用约 40 mm 球径做中心穿越的上界示例：

| 速度示例 | 40 mm 中心遮挡时间示例 |
| ---: | ---: |
| 2 m/s | 20 ms |
| 5 m/s | 8 ms |
| 8 m/s | 5 ms |
| 10 m/s | 4 ms |
| 15 m/s | 2.67 ms |
| 20 m/s | 2 ms |

实际斜向穿越、非中心穿越和球体旋转都会改变 `L_effective`。因此不能仅凭 5 ms 响应参数判断高速乒乓球一定能被捕获。

## 3. 首样测试接法

1. 传感器使用 10–30 V DC 中的受控电源，先记录空载电流和正常遮挡电流。
2. 棕线 `BN(1)` 接电源正端，蓝线 `BU(3)` 接 0 V，黑线 `BK(2)` 通过符合额定值的负载、光耦或晶体管电平转换进入逻辑分析仪/ESP32；不得把 10–30 V 输出直接接 GPIO。
3. 示波器/逻辑分析仪至少同时记录两点：
   - `CH-A`：传感器黑线在负载侧的 NPN 波形；
   - `CH-B`：电平转换后的主控侧波形。
4. 用带参考光电二极管/编码器的电磁快门、细缝转盘或其他能产生已知遮挡宽度的机构，先产生 1–10 ms 的遮挡脉冲；随后再用真实乒乓球做速度和轨迹复测。
5. 首轮只接一对发射/接收器，完成时间测试后再扩展到 10 个通道；边缘通道和交错 y 通道也要抽测，排除机械安装差异。

## 4. 遮挡脉冲矩阵

每个脉宽至少重复 30 次，并分别测试“遮挡”和“恢复光束”两个方向。记录触发参考边沿、NPN 输出变化完成时间、主控侧边沿、输出脉宽、是否漏检和是否有多脉冲。

| 目标遮挡宽度 | 重复次数 | 检出次数 | 漏检次数 | NPN 输出脉宽 | 上升/下降延迟 | 证据 |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 ms | 30 |  |  |  |  |  |
| 2 ms | 30 |  |  |  |  |  |
| 3 ms | 30 |  |  |  |  |  |
| 4 ms | 30 |  |  |  |  |  |
| 5 ms | 30 |  |  |  |  |  |
| 6 ms | 30 |  |  |  |  |  |
| 8 ms | 30 |  |  |  |  |  |
| 10 ms | 30 |  |  |  |  |  |

建议把“`30/30` 检出且无额外脉冲”作为首样可靠性门；最终门槛要根据目标球速下实测的最短 `t_block` 再加机械/速度裕量冻结。若 1–5 ms 区间无法稳定检出，应改用更快的传感器或重新定义检测事件，不能靠软件延长一个不存在的脉冲。

## 5. 真实球验证

在已知遮挡脉冲测试之后，使用目标球和实际过网方向记录：球速、相机/编码器参考、光束高度、球心是否穿越光束、`t_block`、NPN 波形和主控事件。至少覆盖中心穿越、边缘穿越、斜向穿越和不同高度通道。

只有当目标场景中最短实测 `t_block` 在全部重复试验中稳定产生对应输出，才允许关闭当前“球体遮挡宽度/高速漏检”待确认项，并将 B-06 的 M6 通道验收从 `待实机` 推进到下一阶段。

## 6. 证据文件建议

```text
<run>-M6-01-sensor-side-1ms.csv
<run>-M6-02-sensor-side-2ms.csv
<run>-M6-05-sensor-side-5ms.csv
<run>-M6-10-sensor-side-10ms.csv
<run>-M6-ball-speed-and-block.csv
<run>-M6-waveform.jpg
<run>-M6-channel-map.json
```

原始波形必须保留，不能只记录“检测到/未检测到”；现场总记录仍使用 [`field-validation-record-template.zh-CN.md`](field-validation-record-template.zh-CN.md)。

## 7. CSV 分析器

仓库提供 [`tools/analyze_m6_response.py`](../tools/analyze_m6_response.py)，只依赖 Python 标准库。逻辑分析仪导出为以下最小格式后，可以直接生成每次试验的边沿配对、输入/输出脉宽、延迟、漏检和汇总检测率：

```csv
trial_id,time_us,reference,sensor_npn
1,0,0,0
1,1000,1,0
1,6000,1,1
1,8000,0,1
1,9000,0,0
```

运行：

```text
python3 tools/analyze_m6_response.py \
  --input evidence/<run>-M6-waveform.csv \
  --output evidence/<run>-M6-response.json
```

如果还要分析电平转换后的主控侧信号，把列名替换为 `mcu` 并加 `--output-column mcu`。分析器会把未配对的参考边沿记录为漏检，不会用零延迟或软件窗口把它改成通过；配套单元测试为 `python3 tools/test_analyze_m6_response.py`。

收到真实 CSV 前，可用 `python3 tools/test_m6_response_workflow.py` 做一次纯合成的 30 次端到端回归（CSV → 边沿分析 → 批次门）；该测试只验证工具链，不产生实物验收证据。

收到器件后，可先运行 `python3 tools/init_m6_acceptance_run.py --output-dir evidence/<run-id>` 创建不覆盖旧目录的验收骨架；它只生成 `pending` 模板和 CSV 表头，不会伪造任何实物证据。

如果输入的是示波器上的原始 NPN 低有效电平，必须显式加 `--invert-output`：

```text
python3 tools/analyze_m6_response.py \
  --input evidence/<run>-M6-waveform.csv \
  --output evidence/<run>-M6-response.json \
  --invert-output
```

分析器现在要求参考边沿与输出边沿方向一致；未声明极性或方向相反的边沿会被计为漏检/额外边沿，不会静默通过。

对同一个目标遮挡宽度完成至少 30 次后，再用批次门检查“每次都检出且没有额外边沿”：

```text
python3 tools/validate_m6_response_batch.py \
  evidence/<run>-M6-response.json \
  --target-width-us 5000 \
  --min-trials 30 \
  --max-latency-us 20000
```

`--target-width-us` 只是这批快门/遮挡机构的目标输入宽度；它不是传感器的最小遮挡门槛。要关闭高速漏检风险，必须分别对 `1/2/3/4/5/6/8/10 ms` 批次运行并结合真实球的最短 `t_block` 判断。
