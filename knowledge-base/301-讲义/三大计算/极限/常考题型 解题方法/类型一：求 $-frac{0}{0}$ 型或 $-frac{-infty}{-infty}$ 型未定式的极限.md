---
title: 类型一：求 $\frac{0}{0}$ 型或 $\frac{\infty}{\infty}$ 型未定式的极限
date: 2026-05-17T00:00:00+08:00
lastmod: 2026-05-19T10:13:46+08:00
---

# 类型一：求 $\frac{0}{0}$ 型或 $\frac{\infty}{\infty}$ 型未定式的极限

```
``````

## 类型一：求 $\frac{0}{0}$ 型或 $\frac{\infty}{\infty}$ 型未定式的极限

### 【解题方法】

① 拆极限
② 取大头
③ 等价无穷小替换
④ 洛必达法则（务必注意使用的条件与限制！）
⑤ 泰勒公式
⑥ 拉格朗日中值定理

### 【例 1.1】求极限 $\lim_{x \to 0^+} \frac{1 - \sqrt{\cos x}}{x(1 - \cos \sqrt{x})}$ 替换+有理化

![image](assets/image-20260519095059-ft0uqb6.png)

#### 【小崔点睛】

遇到极限的分子、分母中出现 $\sqrt{A} - \sqrt{B}$ 时，可以采取根式有理化进行等价变形，例如 $\sqrt{A} - \sqrt{B} = \frac{A - B}{\sqrt{A} + \sqrt{B}}$。

### 【例 1.2】求极限 $\lim_{x \to 0} \frac{x \cos x - \sin x}{x^3}$

![image](assets/image-20260519095126-n7td2e1.png)

#### 【小崔点睛】

在极限的加减法中，非因式尽量不要直接计算或使用等价无穷小替换，往往替换了就错，精度不够！

### 【例 1.3】求极限 $\lim_{x \to 0} \frac{e^{\tan x} - e^{\arctan x}}{(e^{x^2} - 1) \ln(1+x)}$

#### （一）用标准解法 $e^{\square} - e^{\triangle}$ -> $e^{\triangle} \left( e^{\square - \triangle} - 1 \right)$

![image](assets/image-20260519095240-u6la52t.png)

#### （二）taylor

![image](assets/image-20260519095348-whewrpn.png)

#### （三）拉格朗日定理

![image](assets/image-20260519095421-8fn8b6o.png)

#### 【小崔点睛】

咱们在遇到极限中分子或分母出现 $e^{\square} - e^{\triangle}$ 结构时，可以考虑提公因子后转化为 $e^{\triangle} \left( e^{\square - \triangle} - 1 \right)$ 再进一步处理。

### 【例 1.4】求极限 $\lim_{x \to 0} \frac{\sin(\sin x) - \sin(\tan x)}{x^3}$ 看作整体

#### （一）拉格朗日中值定理

![image](assets/image-20260519095719-avv1xwd.png)

#### （二）复合taylor展开

![image](assets/image-20260519095741-z0su0pi.png)

#### 【小崔点睛】

在遇到极限中分子或分母出现 $f(A) - f(B)$ 时，可以考虑利用拉格朗日中值定理转化为 $f'(\xi)(A - B), \xi \in (A, B)$ 后再去计算.
提醒大家，使用拉格朗日中值定理时，要注意 $\xi$ 是介于 $A, B$ 之间！

### 【例 1.5】求极限 $\lim_{x \to 1} \frac{\ln[\cos(x-1)]}{1 - \sin\left(\frac{\pi}{2}x\right)}$

lnx -> ln(1+(x-1)) -> x-1

![image](assets/image-20260519095902-x907lzs.png)

### 【例 1.6】求极限 $\lim_{x \to \infty} \frac{(x-2)^3 (2x+5)^{30}}{(2x+1)^{33}}$ 取大头

![image](assets/image-20260519095933-7ctvwul.png)

### 【例 1.7】求极限 $\lim_{x \to -\infty} \frac{x+1-\sqrt{4x^2}}{\sqrt{x^2+\sin}}$

取大头 注意看极限的符号去绝对值

![image](assets/image-20260519100001-hdez0v7.png)

#### 【小崔点睛】

本题计算的是 $x \to \infty$ 的极限，对于根号的运算，要小心！当 $x &lt; 0$ 时，$\sqrt{x^2} = -x$

### 

这份文档主要归纳了 **0/0 型** 与  **∞/∞ 型未定式极限** 的系统解法，并配合典型例题展示了不同技巧的灵活运用。我帮你把整体思路、注意事项梳理出来，并逐一解答这些例题，把方法的“为什么”和“怎么用”讲清楚。

---

## 一、整体思路与注意事项

### 六种主流方法（按使用优先级大致排列）

① **等价无穷小替换**：只能用在乘除的**因式**上，**加减法不要直接代换**（精度不够）。  
② **拆极限**：把复杂式子拆成几个独立极限相乘/相除，但必须保证每部分极限存在且不得到 ∞·0 等不定式。  
③ **取大头**：适用于 ∞/∞ 型，分子分母同除以最高阶无穷大，比较次数。  
④ **洛必达法则**：0/0 或 ∞/∞ 时可用，但务必验证条件（可导、导数之比极限存在），有时和等价替换混用更高效。  
⑤ **泰勒公式**：处理复杂函数差时的终极武器，能精确控制保留的阶数，避免“替换了但精度不够”的错误。  
⑥ **拉格朗日中值定理**：遇到 $f(A)-f(B)$ 结构时，可写成 $f'(\xi)(A-B)$，$\xi$ 处于 $A,B$ 之间，注意需说明 $\xi$ 趋向行为。

### 核心注意事项

- **加减法中的等价代换要小心**：必须用泰勒展开确认足够阶数才会安全。
- **遇根式差**：$\sqrt{A}-\sqrt{B}$ 首选有理化。
- **遇指数差**：$e^\square-e^\triangle$ 优先提公因子 $e^\triangle$，转化成 $e^{\square-\triangle}-1$ 再等价。
- **反三角函数、复合函数差**：拉格朗日中值定理或复合泰勒展开都是利器。
- **无界符号**：$x\to-\infty$ 时注意 $\sqrt{x^2}=-x$，绝对值千万别忘。

---

## 二、例题解答（思路 + 详细过程）

### 【例 1.1】

$$
\lim_{x\to 0^+}\frac{1-\sqrt{\cos x}}{x(1-\cos\sqrt{x})}
$$

**方法**：分子有理化 + 等价无穷小替换  
**解**：

$$
1-\sqrt{\cos x} = \frac{1-\cos x}{1+\sqrt{\cos x}} \sim \frac{\frac{x^2}{2}}{1+1}= \frac{x^2}{4}\quad (x\to 0^+)
$$

分母：

$$
x(1-\cos\sqrt{x}) \sim x\cdot\frac{(\sqrt{x})^2}{2} = \frac{x^2}{2}
$$

所以极限为 $\displaystyle \frac{x^2/4}{x^2/2} = \frac12$.

**点睛**：有理化后所有项都变为因式，等价替换合法且精准。

---

### 【例 1.2】

$$
\lim_{x\to 0}\frac{x\cos x - \sin x}{x^3}
$$

**方法一（泰勒，最稳妥）**

$$
\cos x = 1-\frac{x^2}{2}+o(x^2),\quad \sin x = x - \frac{x^3}{6}+o(x^3)
$$

$$
x\cos x = x - \frac{x^3}{2}+o(x^3)
$$

$$
x\cos x - \sin x = \left(-\frac{x^3}{2} + \frac{x^3}{6}\right) + o(x^3) = -\frac{x^3}{3}+o(x^3)
$$

除以 $x^3$ 得 $-\frac13$.

**方法二（洛必达）**   
原是 0/0 型，洛一次：

$$
\frac{\cos x - x\sin x - \cos x}{3x^2} = \frac{-x\sin x}{3x^2} \to -\frac13
$$

（再次使用等价无穷小 $\sin x\sim x$ 在乘除中合法）

**为什么不能直接对** **$x\cos x$** **和** **$\sin x$** **分别等价？**   
因为 $x\cos x$ 和 $\sin x$ 都等价于 $x$，差为 0，但实际差是 $-\frac{x^3}{3}$，等价替换丢失了高阶信息。**加减法替换精度不够，必错。**

---

### 【例 1.3】

$$
\lim_{x\to 0}\frac{e^{\tan x} - e^{\arctan x}}{(e^{x^2}-1)\ln(1+x)}
$$

**方法**：提 $e^{\triangle}$ 转化 + 等价替换  
分母：$e^{x^2}-1\sim x^2$，$\ln(1+x)\sim x$，分母 $\sim x^3$。  
分子：

$$
e^{\tan x} - e^{\arctan x} = e^{\arctan x}\left(e^{\tan x - \arctan x} - 1\right)
$$

$e^{\arctan x}\to 1$，而

$$
\tan x - \arctan x = \left(x+\frac{x^3}{3}+\cdots\right) - \left(x-\frac{x^3}{3}+\cdots\right) = \frac{2}{3}x^3 + o(x^3)
$$

故 $e^{\tan x - \arctan x} - 1 \sim \frac{2}{3}x^3$。  
分子 $\sim \frac{2}{3}x^3$，整体极限 $\frac{2/3}{1} = \frac23$.

**其他解法**：泰勒直接展开 $e^{\tan x}$ 和 $e^{\arctan x}$；或者分子看作 $f(\tan x)-f(\arctan x)$ 用拉格朗日：$f(u)=e^u,\ f'(\xi)=e^\xi\to 1$，差 $\sim (\tan x-\arctan x) \to \frac23 x^3$。

---

### 【例 1.4】

$$
\lim_{x\to 0}\frac{\sin(\sin x) - \sin(\tan x)}{x^3}
$$

**方法一（拉格朗日）**   
令 $f(u)=\sin u$，则

$$
\sin(\sin x) - \sin(\tan x) = f'(\xi)(\sin x - \tan x) = \cos\xi\,(\sin x - \tan x)
$$

其中 $\xi$ 介于 $\sin x$ 与 $\tan x$ 之间。$x\to0$ 时 $\sin x\sim x$，$\tan x\sim x$，故 $\xi\to0$，$\cos\xi\to1$。因此分子等价于 $\sin x - \tan x$。

$$
\sin x - \tan x = \sin x\frac{\cos x-1}{\cos x} \sim x\cdot\frac{-x^2/2}{1} = -\frac{x^3}{2}
$$

故极限为 $-\frac12$.

**方法二（复合泰勒）**

$$
\sin u = u - \frac{u^3}{6}+\cdots
$$

$$
\sin(\sin x) = \sin x - \frac{\sin^3 x}{6}+\cdots = \left(x-\frac{x^3}{6}\right) - \frac{x^3}{6} + o(x^3) = x - \frac{x^3}{3}+o(x^3)
$$

$$
\sin(\tan x) = \tan x - \frac{\tan^3 x}{6}+\cdots = \left(x+\frac{x^3}{3}\right) - \frac{x^3}{6} + o(x^3) = x + \frac{x^3}{6}+o(x^3)
$$

相减得 $-\frac{x^3}{3} - \frac{x^3}{6} = -\frac{x^3}{2}$，除以 $x^3$ 得 $-\frac12$.

**注意**：拉格朗日方法要明确 $\xi$ 与被夹逼变量的关系，确保 $\cos\xi$ 的极限是确定的。

---

### 【例 1.5】

$$
\lim_{x\to 1}\frac{\ln[\cos(x-1)]}{1-\sin\left(\frac{\pi}{2}x\right)}
$$

**换元**：令 $t = x-1 \to 0$。  
分子：

$$
\ln(\cos t) = \ln\left(1 - \frac{t^2}{2} + o(t^2)\right) \sim -\frac{t^2}{2}
$$

分母：

$$
1 - \sin\left(\frac{\pi}{2}(t+1)\right) = 1 - \sin\left(\frac{\pi}{2} + \frac{\pi}{2}t\right) = 1 - \cos\left(\frac{\pi}{2}t\right)
$$

$$
1 - \cos\left(\frac{\pi}{2}t\right) \sim \frac{1}{2}\left(\frac{\pi t}{2}\right)^2 = \frac{\pi^2 t^2}{8}
$$

所以极限为 $\displaystyle \frac{-t^2/2}{\pi^2 t^2/8} = -\frac{4}{\pi^2}$.

**点睛**：非零化零（x→1换成t→0），将复杂结构转为常见等价无穷小。

---

### 【例 1.6】

$$
\lim_{x\to\infty}\frac{(x-2)^3 (2x+5)^{30}}{(2x+1)^{33}}
$$

**方法**：取大头（比较无穷大的阶数）  
分子最高次项：$(x)^3 \cdot (2x)^{30} = 2^{30}x^{33}$。  
分母最高次项：$(2x)^{33} = 2^{33}x^{33}$。  
极限为 $\displaystyle \frac{2^{30}}{2^{33}} = \frac18$.

具体操作可同除以 $x^{33}$。

---

### 【例 1.7】

$$
\lim_{x\to -\infty}\frac{x+1-\sqrt{4x^2}}{\sqrt{x^2+\sin x}}
$$

**方法**：取大头 + 注意绝对值  
$x\to -\infty$ 时，$\sqrt{x^2} = -x$，$\sqrt{4x^2}=2|x| = -2x$。  
分子：

$$
x+1 - \sqrt{4x^2} = x+1 - (-2x) = 3x+1
$$

分母：

$$
\sqrt{x^2+\sin x} = \sqrt{x^2\left(1+\frac{\sin x}{x^2}\right)} = |x|\sqrt{1+\frac{\sin x}{x^2}} = -x\sqrt{1+\frac{\sin x}{x^2}}
$$

因为 $\frac{\sin x}{x^2}\to 0$，分母 $\sim -x$。  
故原式 $\sim \frac{3x}{-x} = -3$（准确写为 $\frac{3x+1}{-x}\to -3$）。

**极易出错的点**：$\sqrt{x^2}=x$ 是仅在 $x\ge 0$ 成立；$x<0$ 时必须是 $-x$。无穷远处根号下带平方，符号一错全盘皆输。

---

## 三、总结性看法

- 文档把这些经典题目按方法归类，背后的逻辑是  **“先化简结构，再消灭未定式”** 。
- 等价无穷小是最快武器，但必须严格限于因式；一旦有加减，请泰勒或拉格朗日帮忙。
- 洛必达是通用工具，但不是万能，使用前先看是否有更简单的等价替换可做，以及是否满足条件。
- 最后的“取大头”用来解决 ∞/∞ 多项式/根式比阶，关键细节在于 $\sqrt{x^2}$ 绝对值的处理。

如果你愿意，我可以进一步针对某类方法（比如泰勒展开什么时候展开到几阶）再给出专项训练。

‍

# 泰勒展开“展到几阶”专项训练

泰勒公式是做极限题最强大的工具之一，但初学者最头疼的就是：**到底展开到第几项？**   
这个专项训练帮你彻底搞清判断规则。

---

## 一、核心原则：“上下同阶”原则

> **原则**：分子和分母展开后，**保留到它们的首个非零最低次项足以判断极限为止**。  
> 用公式讲，就是：
>
> - 如果是分式 $\frac{A(x)}{B(x)}$，且知道分母的阶数（比如分母是 $x^k$），那就把分子展开到 **$x^k$** **的精确阶**（也就是展开到 $x^k$，并且 $x^k$ 项系数不能为 0）。
> - 如果是加减法 $f(x)-g(x)$，要展开到**两项差中第一次出现的不为零的那一阶**。

更具体的两条操作性规则：

### 规则 1：分母为 $x^k$，分子就展到 $x^k$

若极限形式为

$$
\lim_{x\to0}\frac{f(x)}{x^k}
$$

只需将 $f(x)$ 展开到 **$x^k$** **项**（包括写 $o(x^k)$），因为低于 $k$ 次的项除以 $x^k$ 会发散或无意义，高于 $k$ 次的项除以 $x^k$ 会趋于 0，不起作用。

### 规则 2：加减法中展到“消不掉”的第一次非零阶

比如 $f(x)-g(x)$，如果分别展开后，**低阶项恰好抵消**（系数互为相反数），就必须继续展到下一阶，直到两个展开式差的第一个非零项出现为止。

---

## 二、经典例子验证规则

### 例 1：分母定阶，直接展到该阶

$$
\lim_{x\to0}\frac{e^x - \sin x - 1}{x^2}
$$

分母是 $x^2$，我们要将分子展到 $x^2$。

$$
e^x = 1 + x + \frac{x^2}{2} + o(x^2)
$$

$$
\sin x = x - \frac{x^3}{6} + o(x^3) \quad\leftarrow\text{注意这里 sine 无 }x^2\text{ 项}
$$

分子展开：

$$
(1+x+\frac{x^2}{2}) - (x) - 1 = \frac{x^2}{2} + o(x^2)
$$

除以 $x^2$ 得 $\frac12$。  
显然，若只展到 $x^1$，得 $1+x - x - 1 = 0$，无法判断，说明精度不够。

---

### 例 2：抵消需要多展一阶

$$
\lim_{x\to0}\frac{\tan x - \sin x}{x^3}
$$

分母 $x^3$，按说分子应展到 $x^3$，我们试试：

$$
\tan x = x + \frac{x^3}{3} + o(x^3),\quad
\sin x = x - \frac{x^3}{6} + o(x^3)
$$

相减得：

$$
\tan x - \sin x = \left(x + \frac{x^3}{3}\right) - \left(x - \frac{x^3}{6}\right) = \frac{x^3}{2} + o(x^3)
$$

极限为 $\frac12$。  
为什么展到三阶？正是因为一阶的 $x$ 项抵消了，所以必须展到第一次不抵消的阶（这里是三阶）。**这完全符合“上下同阶”和“抵消继续”的思路。**

---

### 例 3：复杂复合函数

$$
\lim_{x\to0}\frac{\ln(1+x+\frac{x^2}{2}) - x}{x^2}
$$

分母 $x^2$，把分子的对数展开到 $x^2$。  
注意 $\ln(1+u)=u-\frac{u^2}{2}+o(u^2)$，而 $u=x+\frac{x^2}{2}=x+\frac{x^2}{2}+o(x^2)$。  
则

$$
\begin{aligned}
u^2 &= \left(x+\frac{x^2}{2}\right)^2 = x^2 + x^3 + \frac{x^4}{4} = x^2 + o(x^2) \quad(\text{只保留到 }x^2\text{项})
\end{aligned}
$$

于是

$$
\ln(1+u) = \left(x+\frac{x^2}{2}\right) - \frac{1}{2}(x^2) + o(x^2) = x + \frac{x^2}{2} - \frac{x^2}{2} + o(x^2) = x + o(x^2)
$$

分子 $= x + o(x^2) - x = o(x^2)$，极限为 0。  
恰好到 $x^2$ 有效。

---

## 三、口诀总结

> **分式型**：分母几阶，分子就展到几阶；  
> **减法型**：一旦同阶相消，立刻再加一阶；  
> **乘法型**：每个因子展到保证乘积达到要求阶数；  
> **小心复合**：内层展到足以让外层展开到所需阶数为止。

---

## 四、专项训练题（附答案与解析）

**题 1**

$$
\lim_{x\to0}\frac{\cos x - e^{-x^2/2}}{x^4}
$$

<details>  
<summary>答案与解析</summary>

分母 $x^4$，展分子到 $x^4$。

$$
\cos x = 1 - \frac{x^2}{2} + \frac{x^4}{24} + o(x^4)
$$

$$
e^{-x^2/2} = 1 - \frac{x^2}{2} + \frac{x^4}{8} + o(x^4)
$$

相减：

$$
\cos x - e^{-x^2/2} = \left(1 - \frac{x^2}{2} + \frac{x^4}{24}\right) - \left(1 - \frac{x^2}{2} + \frac{x^4}{8}\right) = \left(\frac{1}{24}-\frac{1}{8}\right)x^4 + o(x^4) = -\frac{x^4}{12} + o(x^4)
$$

极限为 $-\frac{1}{12}$。  
若只展到 $x^2$，则二项完全相同抵消为 0，必须到四阶。  
</details>

---

**题 2**

$$
\lim_{x\to0}\frac{\arcsin x - \arctan x}{x^3}
$$

<details>  
<summary>答案与解析</summary>

分母 $x^3$，展到 $x^3$。

$$
\arcsin x = x + \frac{x^3}{6} + o(x^3),\quad
\arctan x = x - \frac{x^3}{3} + o(x^3)
$$

相减得 $\frac{x^3}{6} - (-\frac{x^3}{3}) = \frac{x^3}{2}$，极限 $\frac12$。  
</details>

---

**题 3**（抵消高阶检测）

$$
\lim_{x\to0}\frac{\tan x - x}{x^3}
$$

<details>  
<summary>答案与解析</summary>

$\tan x = x + \frac{x^3}{3} + o(x^3)$，所以 $\tan x - x = \frac{x^3}{3} + o(x^3)$，一阶抵消，三阶首次非零，极限 $\frac13$。  
</details>

---

**题 4**（复合函数）

$$
\lim_{x\to0}\frac{e^{\sin x} - 1 - x}{x^2}
$$

<details>  
<summary>答案与解析</summary>

分母 $x^2$，将 $e^{\sin x}$ 展到 $x^2$。

$$
\sin x = x - \frac{x^3}{6} + o(x^3)
$$

$$
e^{\sin x} = 1 + \sin x + \frac{\sin^2 x}{2} + o(\sin^2 x)
$$

将 $\sin x$ 代入并只保留到 $x^2$ 项：

$$
\sin x = x + o(x), \quad \sin^2 x = x^2 + o(x^2)
$$

所以 $e^{\sin x} = 1 + x + \frac{x^2}{2} + o(x^2)$。  
分子：$e^{\sin x} - 1 - x = \frac{x^2}{2} + o(x^2)$，极限 $\frac12$。  
注意：$\sin x$ 展到一阶就够，但因平方的存在自然到二阶。  
</details>

---

**题 5**（乘法需协调）

$$
\lim_{x\to0}\frac{(1+x)^{1/x} - e}{x}
$$

<details>  
<summary>答案与解析</summary>

这是个经典难题。  
令 $y=(1+x)^{1/x} = e^{\frac{\ln(1+x)}{x}}$，分母是 $x$，需要展到 1 阶。

$$
\ln(1+x) = x - \frac{x^2}{2} + \frac{x^3}{3} - \cdots
$$

$$
\frac{\ln(1+x)}{x} = 1 - \frac{x}{2} + \frac{x^2}{3} - \cdots
$$

$$
e^{\frac{\ln(1+x)}{x}} = e^{1 - \frac{x}{2} + \cdots} = e \cdot e^{-\frac{x}{2} + \cdots} = e\left(1 - \frac{x}{2} + o(x)\right)
$$

因此分子 $= e\left(1 - \frac{x}{2}\right) - e + o(x) = -\frac{e}{2}x + o(x)$，极限 $-\frac{e}{2}$。  
这里看起来好像在指数上保留到一阶，其实非常考验展开的衔接，需要细心。  
</details>

---

**题 6**（无穷小替换后仍需展开）

$$
\lim_{x\to0}\frac{\ln\frac{1+x}{1-x} - 2x}{x^3}
$$

<details>  
<summary>答案与解析</summary>

分母 $x^3$。

$$
\ln\frac{1+x}{1-x} = \ln(1+x) - \ln(1-x)
$$

$$
= \left[x - \frac{x^2}{2} + \frac{x^3}{3} - \frac{x^4}{4} + \cdots\right] - \left[-x - \frac{x^2}{2} - \frac{x^3}{3} - \frac{x^4}{4} - \cdots\right]
$$

$$
= 2x + \frac{2}{3}x^3 + o(x^3)
$$

所以分子 $= \frac{2}{3}x^3 + o(x^3)$，极限 $\frac{2}{3}$。  
一阶项恰好和后面的 $-2x$ 抵消，保证了必须展到三阶。  
</details>

---

## 五、实战口诀（再强化）

1. **一看分母阶数** → 决定展开截止项数；
2. **展完后检查加减** → 如果一阶项（或某阶）系数全为零，立即多展一阶；
3. **复合函数** → 从内向外，保证代入外层后不丢失关键阶数；
4. **乘除因式** → 可以各自独立展开，再相乘截断到所需阶数。

---

你可以拿这 6 道题当自我检测。如果遇到具体展开不确定的题目，欢迎继续拿出来，我们实战分析一遍。
