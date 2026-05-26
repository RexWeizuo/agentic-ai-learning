---
title: 类型二：求 $0\cdot\infty$ 型或 $\infty-\infty$ 型未定式的极限
date: 2026-05-17T00:00:00+08:00
lastmod: 2026-05-19T10:43:00+08:00
---

# 类型二：求 $0\cdot\infty$ 型或 $\infty-\infty$ 型未定式的极限

```
``````

## 类型二：求 $0\cdot\infty$ 型或 $\infty-\infty$ 型未定式的极限

### 【解题方法】

① 求 $0\cdot\infty$ 型未定式的极限并不复杂，只需要根据函数的特点先将 $0\cdot\infty$ 型未定式转化为 $\frac{0}{0}$ 型或 $\frac{\infty}{\infty}$ 型未定式后，再根据相应的计算方法来处理. 而且，咱们通常需要将 $0\cdot\infty$ 型里复杂的因子部分用作分子.

② 求 $\infty-\infty$ 型未定式的极限需要通过适当的方法将其转化为 $\frac{0}{0}$ 型或 $\frac{\infty}{\infty}$ 型未定式.

常见的有三类情况：
1、 $\infty-\infty$ 型未定式是两个分式函数之差，可通分化为 $\frac{0}{0}$ 型或 $\frac{\infty}{\infty}$ 型未定式；
2、 $\infty-\infty$ 型未定式是两个根式函数之差，可利用根式有理化将其转化；
3、 若函数不是分式，可尝试利用换元 $x=\frac{1}{t}$，处理为分式后再通分转化.

### 【例 1.8】求极限 $\lim_{x\to\infty}x^2\left[\frac{\pi}{2}-\arctan(2x^2)\right]$ 最好就是洛 或者u>0用反三角恒等式

‍

### 【例 1.9】求极限 $\lim_{x\to0}\left(\frac{1}{\sin^2x}-\frac{1}{x^2\cos^2x}\right)$

![image](assets/image-20260519103817-99gbk4l.png)

### 【例 1.10】求极限 $\lim_{x \to \infty} \left[ (x^2 - x)e^{\frac{1}{x}} - \sqrt{x^4 + x^2} \right]$

**分析**：$\infty-\infty$ 型，不是分式结构，最适合**倒代换** $t=1/x$。

![image](assets/image-20260519104059-ar60k0p.png)

### 【例 1.11】极限 $\lim_{n \to \infty} n \tan(\pi \sqrt{n^2 + n})$

![image](assets/image-20260519104300-ljfn6s9.png)

遇到三角函数类的极限计算，出现 $\sin(\square), \cos(\square), \tan(\square) \to 0$ 但 $\square$ 并非趋于 $0$ 时，咱们可以利用三角函数的周期性质来化简计算！

‍

这份文档聚焦于 **$0\cdot\infty$** **型** 和 **$\infty-\infty$** **型** 未定式极限。核心思想只有一个：**通过恒等变形，把它们转化成熟悉的** **$\frac{0}{0}$** **型或** **$\frac{\infty}{\infty}$** **型，再用类型一的方法解决。**

---

## 一、整体思路与转化策略

### 1.  $0\cdot\infty$ 型

**转化方法**：把其中**较复杂的一个因子放到分母**（取倒数），就能变成

$$
0\cdot\infty \;\longrightarrow\; \frac{0}{0} \quad\text{或}\quad \frac{\infty}{\infty}
$$

例如 $x^2\left(\frac{\pi}{2}-\arctan(2x^2)\right)$，把 $x^2$ 写成 $1/(1/x^2)$，就变成 $\frac{0}{0}$。  
**注意**：通常选择**简单因子取倒数**当分母（如多项式），分子保留较复杂的因子，这样求导或展开更方便。

### 2.  $\infty-\infty$ 型

三件法宝：

- **通分**（分式差） $\longrightarrow$ 合并成一个分式；
- **有理化**（根式差） $\longrightarrow$ 利用 $\sqrt{A}-\sqrt{B}=\frac{A-B}{\sqrt{A}+\sqrt{B}}$ 消去根号；
- **倒代换** $x=\frac1t$（非分式） $\longrightarrow$ 变成分式后再通分。

转化后都是 $\frac{0}{0}$ 或 $\frac{\infty}{\infty}$，接着就可以等价替换、泰勒展开或洛必达。

---

## 二、例题详解 + 点睛

### 【例 1.8】

$$
\lim_{x\to\infty} x^2\left[\frac{\pi}{2}-\arctan(2x^2)\right]
$$

**分析**：  
$x^2\to\infty$，$\arctan(2x^2)\to\frac{\pi}{2}$，括号内趋于 0，属 $\infty\cdot0$。

**解法一（巧用反三角恒等式）(算了还是老老实实算吧)**   
当 $u>0$ 时，$\frac{\pi}{2}-\arctan u = \arctan\frac1u$。  
令 $u=2x^2$，得

$$
\frac{\pi}{2}-\arctan(2x^2) = \arctan\frac{1}{2x^2} \sim \frac{1}{2x^2}\quad (x\to\infty)
$$

于是原式

$$
x^2\cdot\frac{1}{2x^2} = \frac12.
$$

**解法二（转化为** **$\frac{0}{0}$** **洛必达）**   
原式 $= \lim_{x\to\infty}\dfrac{\frac{\pi}{2}-\arctan(2x^2)}{1/x^2}$，洛一次：

$$
\lim_{x\to\infty}\frac{-\frac{1}{1+4x^4}\cdot 4x}{-2/x^3} = \lim_{x\to\infty}\frac{4x}{1+4x^4}\cdot\frac{x^3}{2} = \lim_{x\to\infty}\frac{2x^4}{1+4x^4} = \frac12.
$$

 **【点睛】**   
见到 $\frac{\pi}{2}-\arctan u$ 第一时间想到 $\arctan\frac1u$，瞬间等价无穷小解决战斗，避开繁复求导。

---

### 【例 1.9】

$$
\lim_{x\to0}\left(\frac{1}{\sin^2x}-\frac{1}{x^2\cos^2x}\right)
$$

**分析**：两项均 $\to\infty$，$\infty-\infty$ 型，通分。

**解**：

$$
\text{原式}=\frac{x^2\cos^2x-\sin^2x}{x^2\sin^2x\cos^2x}
$$

分母 $\sim x^2\cdot x^2\cdot 1 = x^4$。  
分子用泰勒展开（展到 4 阶）：

$$
\cos x = 1-\frac{x^2}{2}+o(x^2),\quad
\cos^2x = 1-x^2+o(x^2)
$$

$$
\Rightarrow x^2\cos^2x = x^2 - x^4 + o(x^4)
$$

$$
\sin^2x = \left(x-\frac{x^3}{6}+o(x^3)\right)^2 = x^2 - \frac{x^4}{3}+o(x^4)
$$

分子：

$$
(x^2 - x^4) - \left(x^2 - \frac{x^4}{3}\right) = -\frac{2}{3}x^4 + o(x^4)
$$

所以极限

$$
\frac{-\frac23 x^4}{x^4} = -\frac23.
$$

 **【点睛】**

- 通分后分母主阶明显，分子直接泰勒展开，比洛必达轻松。
- 千万不要只展到二阶就停，这里分子相减消去了 $x^2$ 项，必须展到四位精确度。

---

### 【例 1.10】

$$
\lim_{x\to\infty} \left[ (x^2-x)e^{\frac1x} - \sqrt{x^4+x^2} \right]
$$

**分析**：$\infty-\infty$ 型，不是分式结构，最适合**倒代换** $t=1/x$。

**解**：令 $t=\frac1x$，则 $x\to\infty$ 时 $t\to0$（此处默认 $x\to+\infty$，若 $x\to\infty$ 含负号同理可得相同结果），

$$
x^2-x = \frac{1}{t^2}-\frac{1}{t},\quad
e^{\frac1x}=e^t,\quad
\sqrt{x^4+x^2} = \sqrt{\frac1{t^4}+\frac1{t^2}} = \frac1{t^2}\sqrt{1+t^2}
$$

原式变为

$$
\left(\frac{1}{t^2}-\frac{1}{t}\right)e^t - \frac1{t^2}\sqrt{1+t^2}
= \frac{1}{t^2}\Big[(1-t)e^t - \sqrt{1+t^2}\Big]
$$

分母主阶 $t^2$，分子方括号在 $t\to0$ 时为 0，转化为 $\frac00$ 型。展开：

$$
e^t = 1+t+\frac{t^2}{2}+\frac{t^3}{6}+o(t^3)
$$

$$
(1-t)e^t = (1-t)\left(1+t+\frac{t^2}{2}+\frac{t^3}{6}\right) + o(t^3) = 1 - \frac{t^2}{2} - \frac{t^3}{3} + o(t^3)
$$

$$
\sqrt{1+t^2} = 1 + \frac12 t^2 - \frac18 t^4 + o(t^4)
$$

所以

$$
(1-t)e^t - \sqrt{1+t^2} = \left(1 - \frac{t^2}{2} - \frac{t^3}{3}\right) - \left(1 + \frac12 t^2\right) + o(t^3) = -t^2 - \frac{t^3}{3} + o(t^3)
$$

代回：

$$
\frac{1}{t^2}\cdot(-t^2 + \text{高阶}) \to -1.
$$

 **【点睛】**

- $x\to\infty$ 时结构混乱，倒代换统一到 $t\to0$，立刻清除“无穷大恐惧症”。
- 展开时注意分母是 $t^2$，分子必须保留到二阶（这里三阶也出现但无关），精度不可少。

---

### 【例 1.11】

$$
\lim_{n\to\infty} n\tan\left(\pi\sqrt{n^2+n}\right)
$$

**分析**：这里 $n$ 是正整数趋于无穷。直接用周期化简。

**解**：利用 $\tan(\theta+n\pi)=\tan\theta$。

$$
\pi\sqrt{n^2+n} = \pi n\sqrt{1+\frac1n} = \pi n\left(1+\frac1{2n}-\frac1{8n^2}+\cdots\right) = n\pi + \frac{\pi}{2} - \frac{\pi}{8n} + \cdots
$$

所以

$$
\tan\left(\pi\sqrt{n^2+n}\right) = \tan\left(n\pi + \frac{\pi}{2} - \frac{\pi}{8n} + \cdots\right) = \tan\left(\frac{\pi}{2} - \frac{\pi}{8n} + \cdots\right)
$$

当 $n\to\infty$ 时，括号内的角度从左侧趋近 $\frac{\pi}{2}$，$\tan$ 值趋于 $+\infty$。  
更精确：用 $\tan(\frac{\pi}{2}-\alpha) = \cot\alpha$，

$$
\tan\left(\frac{\pi}{2} - \frac{\pi}{8n}\right) = \cot\left(\frac{\pi}{8n}\right) \sim \frac{1}{\pi/(8n)} = \frac{8n}{\pi}
$$

因此

$$
n \cdot \tan\left(\pi\sqrt{n^2+n}\right) \sim n \cdot \frac{8n}{\pi} = \frac{8n^2}{\pi} \to +\infty.
$$

极限为 $+\infty$ (或写作 “极限不存在，趋于正无穷”)。

 **【点睛】**

- 三角函数里出现 $n\pi + \text{常数}$ 的形式，先用周期性把 $n\pi$ 扔掉，往往能化出 $\frac{\pi}{2}$ 附近的量，再用诱导公式变成 $\cot$ 或 $-\cot$，最后等价无穷小。
- 本题结果虽是无穷大，但思路完全规范：**周期化→诱导→等价代换**，比盲目泰勒更直接。

---

## 三、最后总结

- **转化是核心**：$0\cdot\infty$ 和 $\infty-\infty$ 本身没有直接的极限法则，必须变形。
- **保持“小的结构”** ：尽可能把表达式统一到 $t\to0$ 的情形（倒代换、换元），因为此时等价无穷小、泰勒展开最丰富。
- **精度意识**：通分、有理化后，分子往往出现项与项相消，展开展开时务必展到足够高的阶数。
- **特殊函数技巧**：反三角恒等式、三角函数周期性等能极大简化问题，碰到 $\frac{\pi}{2}-\arctan$、$\tan(n\pi+\cdot)$ 要条件反射式地化简。

掌握这些转化路线，类型二的题目几乎都能流畅地做出来。
