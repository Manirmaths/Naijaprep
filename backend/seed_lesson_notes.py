#!/usr/bin/env python3
"""
Seed/update the lesson_note table with hand-written lesson notes.

Written directly (not generated via OpenAI) -- the content below is
authored and fact-checked worked-example by worked-example, and saved as
"draft", same as everywhere else in the app that treats exam content as
needing a human skim before it's visible to students. Review and publish
each topic from Admin -> Lesson notes. Safe to re-run: upserts by
(subject, topic), so running this again after editing NOTES below just
updates the matching rows instead of duplicating them (and resets them to
draft, since refreshed content deserves a fresh look before going live
again).

Currently covers the Mathematics pilot (10 topics). Add more subjects by
appending additional dicts to NOTES.

Usage:
    python -u seed_lesson_notes.py "<DATABASE_URL>"
    python -u seed_lesson_notes.py "<DATABASE_URL>" --dry-run

Examples:
    python -u seed_lesson_notes.py "sqlite:///./naijaprep.db"
    python -u seed_lesson_notes.py "postgresql://user:pass@host/dbname?sslmode=require"
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import LessonNote

NOTES = [
    {
        "subject": "Mathematics",
        "topic": "Algebraic Processes",
        "title": "Algebraic Processes",
        "summary": "How to expand, factorize, and solve algebraic expressions and equations -- the toolkit almost every other Mathematics topic builds on.",
        "glossary": [
            {"term": "Term", "definition": "a single number, variable, or product of numbers and variables, e.g. \\(3x^2\\)"},
            {"term": "Factorization", "definition": "writing an expression as a product of simpler factors"},
            {"term": "Coefficient", "definition": "the number multiplying a variable, e.g. 5 in \\(5x\\)"},
            {"term": "Simultaneous equations", "definition": "two or more equations solved together for the same unknowns"},
            {"term": "Quadratic equation", "definition": "an equation where the highest power of the unknown is 2"},
        ],
        "content_md": r"""## Expansion and simplification

To simplify an algebraic expression, collect like terms (terms with the same variable and power) and combine them.

Example 1: Simplify \(3x + 5y - x + 2y\).
Group like terms: \((3x - x) + (5y + 2y) = 2x + 7y\).

To expand brackets, multiply every term inside by what's outside.

Example 2: Expand \((x + 3)(x - 5)\).
Multiply each term in the first bracket by each term in the second: \(x\cdot x + x\cdot(-5) + 3\cdot x + 3\cdot(-5) = x^2 - 5x + 3x - 15 = x^2 - 2x - 15\).

## Factorization

There are four common patterns JAMB tests:

- **Common factor**: take out what every term shares, e.g. \(6x^2 + 9x = 3x(2x + 3)\).
- **Difference of two squares**: \(a^2 - b^2 = (a+b)(a-b)\).
- **Quadratic trinomials**: \(x^2 + bx + c\) factorizes as \((x+p)(x+q)\) where \(p+q=b\) and \(pq=c\).
- **Grouping**: split a four-term expression into two pairs that each have a common factor.

Example 3: Factorize \(x^2 + 7x + 12\).
Find two numbers that multiply to 12 and add to 7: 3 and 4. So \(x^2 + 7x + 12 = (x+3)(x+4)\).

Example 4: Factorize \(x^2 - 9\).
This is a difference of two squares: \(x^2 - 9 = (x-3)(x+3)\).

## Linear equations

A linear equation has the unknown to the power of 1. Solve by getting the unknown alone on one side.

Example 5: Solve \(3x - 4 = 11\).
Add 4 to both sides: \(3x = 15\). Divide by 3: \(x = 5\).

## Simultaneous equations

When two equations share two unknowns, solve them together by elimination or substitution.

Example 6: Solve \(x + y = 7\) and \(2x - y = 2\).
Add the two equations to eliminate \(y\): \(3x = 9\), so \(x = 3\). Substitute back: \(3 + y = 7\), so \(y = 4\).

## Quadratic equations

A quadratic can be solved by factorization, completing the square, or the quadratic formula: \(x = \dfrac{-b \pm \sqrt{b^2 - 4ac}}{2a}\) for \(ax^2+bx+c=0\).

Example 7: Solve \(x^2 - 5x + 6 = 0\).
Factorize: \((x-2)(x-3) = 0\), so \(x = 2\) or \(x = 3\).

Example 8: Solve \(2x^2 + 3x - 2 = 0\) using the formula.
Here \(a=2, b=3, c=-2\). \(x = \dfrac{-3 \pm \sqrt{9+16}}{4} = \dfrac{-3\pm5}{4}\), giving \(x = \dfrac{1}{2}\) or \(x = -2\).""",
        "related_topics": ["Inequalities, Permutation, and Combination", "Sequences, Series, and Variation", "Number, Fractions, and Approximation"],
    },
    {
        "subject": "Mathematics",
        "topic": "Calculus",
        "title": "Calculus",
        "summary": "The mathematics of rates of change (differentiation) and accumulation (integration) -- JAMB mostly tests polynomial functions.",
        "glossary": [
            {"term": "Derivative", "definition": "the rate of change of a function, written \\(\\frac{dy}{dx}\\) or \\(f'(x)\\)"},
            {"term": "Gradient", "definition": "the slope of a curve at a point, equal to the derivative there"},
            {"term": "Turning point", "definition": "a point where the gradient is zero -- a maximum or minimum"},
            {"term": "Integration", "definition": "the reverse process of differentiation, used to find area under a curve"},
            {"term": "Stationary point", "definition": "another name for a turning point, where \\(f'(x)=0\\)"},
        ],
        "content_md": r"""## Differentiation

To differentiate \(x^n\), multiply by the power and reduce the power by 1: \(\dfrac{d}{dx}(x^n) = nx^{n-1}\). A constant differentiates to 0.

Example 1: Differentiate \(y = 3x^4 - 2x^2 + 5x - 7\).
Apply the rule to each term: \(\dfrac{dy}{dx} = 12x^3 - 4x + 5\).

## Finding the gradient at a point

Once you have the derivative, substitute the x-value to get the gradient there.

Example 2: Find the gradient of \(y = x^2 - 3x\) at \(x = 2\).
\(\dfrac{dy}{dx} = 2x - 3\). At \(x=2\): gradient \(= 2(2) - 3 = 1\).

## Turning points (maxima and minima)

A curve is momentarily flat at a turning point, so its gradient is zero there.

Example 3: Find the turning point of \(y = x^2 - 4x + 1\).
Differentiate: \(\dfrac{dy}{dx} = 2x - 4\). Set to zero: \(2x - 4 = 0\), so \(x = 2\). Substitute back: \(y = 4 - 8 + 1 = -3\). The turning point is \((2, -3)\).

To tell whether it's a maximum or minimum, check the second derivative: if \(\dfrac{d^2y}{dx^2} > 0\) it's a minimum; if negative, a maximum. Here \(\dfrac{d^2y}{dx^2} = 2\), which is positive, so \((2,-3)\) is a minimum.

## Integration

Integration reverses differentiation: raise the power by 1 and divide by the new power, then add a constant \(C\): \(\displaystyle\int x^n\,dx = \dfrac{x^{n+1}}{n+1} + C\).

Example 4: Integrate \(6x^2 - 4x + 3\).
\(\displaystyle\int (6x^2 - 4x + 3)\,dx = 2x^3 - 2x^2 + 3x + C\).

Example 5: Evaluate \(\displaystyle\int_1^3 (2x + 1)\,dx\).
Integrate first: \(x^2 + x\). Substitute the limits: \((9+3) - (1+1) = 12 - 2 = 10\).""",
        "related_topics": ["Algebraic Processes", "Coordinate Geometry and Trigonometry", "Sequences, Series, and Variation"],
    },
    {
        "subject": "Mathematics",
        "topic": "Commercial Arithmetic",
        "title": "Commercial Arithmetic",
        "summary": "Percentages applied to money -- interest, profit/loss, discount, and ratio are the JAMB favourites.",
        "glossary": [
            {"term": "Principal", "definition": "the original sum of money before interest is added"},
            {"term": "Simple interest", "definition": "interest calculated only on the original principal each year"},
            {"term": "Compound interest", "definition": "interest calculated on the principal plus any interest already earned"},
            {"term": "Profit/loss percent", "definition": "profit or loss expressed as a percentage of the cost price"},
            {"term": "Depreciation", "definition": "the reduction in an asset's value over time"},
        ],
        "content_md": r"""## Simple interest

Simple interest: \(I = \dfrac{PRT}{100}\), where \(P\) = principal, \(R\) = rate per year (%), \(T\) = time in years.

Example 1: Find the simple interest on ₦50,000 for 3 years at 6% per annum.
\(I = \dfrac{50000 \times 6 \times 3}{100} = 9000\). The interest is ₦9,000.

## Compound interest

Compound interest: \(A = P\left(1+\dfrac{R}{100}\right)^T\), where \(A\) is the final amount.

Example 2: Find the compound amount on ₦20,000 for 2 years at 5% per annum.
\(A = 20000(1.05)^2 = 20000 \times 1.1025 = 22050\). The amount is ₦22,050, so the interest earned is ₦2,050.

## Profit and loss

Percentage profit \(= \dfrac{\text{Profit}}{\text{Cost price}} \times 100\); percentage loss works the same way using the loss.

Example 3: A trader buys a bag for ₦4,000 and sells it for ₦4,800. Find the percentage profit.
Profit \(= 4800 - 4000 = 800\). Percentage profit \(= \dfrac{800}{4000}\times100 = 20\%\).

## Discount and commission

Discount is a reduction off the marked price; commission is a percentage of sales paid to an agent. Both are calculated the same way as percentage profit -- as a percentage of a base value.

Example 4: An item marked ₦15,000 is sold at a 10% discount. Find the selling price.
Discount \(= 10\% \times 15000 = 1500\). Selling price \(= 15000 - 1500 = 13500\).

## Ratio, proportion, and rate

Quantities in a ratio share a total in proportion to their ratio parts.

Example 5: Share ₦36,000 between two partners in the ratio 4:5.
Total parts \(= 4+5 = 9\). First share \(= \dfrac{4}{9}\times36000 = 16000\); second share \(= \dfrac{5}{9}\times36000 = 20000\).""",
        "related_topics": ["Number, Fractions, and Approximation", "Sequences, Series, and Variation", "Statistics and Probability"],
    },
    {
        "subject": "Mathematics",
        "topic": "Coordinate Geometry and Trigonometry",
        "title": "Coordinate Geometry and Trigonometry",
        "summary": "Describing lines and points with coordinates, and relating angles to side lengths in triangles.",
        "glossary": [
            {"term": "Gradient", "definition": "the steepness of a line, \\(m = \\dfrac{y_2-y_1}{x_2-x_1}\\)"},
            {"term": "Midpoint", "definition": "the point exactly halfway between two given points"},
            {"term": "Sine, cosine, tangent", "definition": "ratios of a right triangle's sides relative to an angle"},
            {"term": "Angle of elevation", "definition": "the angle you look up through from the horizontal to see an object above you"},
            {"term": "Bearing", "definition": "a direction measured clockwise from North, given as three digits, e.g. \\(065°\\)"},
        ],
        "content_md": r"""## Distance, midpoint, and gradient

Distance between \((x_1,y_1)\) and \((x_2,y_2)\): \(d = \sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}\).
Midpoint: \(\left(\dfrac{x_1+x_2}{2}, \dfrac{y_1+y_2}{2}\right)\).
Gradient: \(m = \dfrac{y_2-y_1}{x_2-x_1}\).

Example 1: Find the distance and midpoint between \((1,2)\) and \((4,6)\).
Distance \(= \sqrt{(4-1)^2+(6-2)^2} = \sqrt{9+16} = \sqrt{25} = 5\). Midpoint \(= \left(\dfrac{1+4}{2}, \dfrac{2+6}{2}\right) = (2.5, 4)\).

## Equation of a line

The equation of a line through \((x_1,y_1)\) with gradient \(m\) is \(y - y_1 = m(x - x_1)\). Parallel lines have equal gradients; perpendicular lines have gradients that multiply to \(-1\).

Example 2: Find the equation of the line through \((2,3)\) with gradient 4.
\(y - 3 = 4(x-2)\), which simplifies to \(y = 4x - 5\).

## Trigonometric ratios

In a right triangle, for a chosen angle: \(\sin\theta = \dfrac{\text{opposite}}{\text{hypotenuse}}\), \(\cos\theta = \dfrac{\text{adjacent}}{\text{hypotenuse}}\), \(\tan\theta = \dfrac{\text{opposite}}{\text{adjacent}}\). Remember this as SOHCAHTOA.

Example 3: A ladder leans against a wall, making a 60° angle with the ground, and reaches 8m up the wall. Find the ladder's length.
\(\sin 60° = \dfrac{8}{\text{ladder}}\), so ladder \(= \dfrac{8}{\sin 60°} \approx \dfrac{8}{0.866} \approx 9.24\)m.

## Sine and cosine rule

For any triangle (not just right-angled): sine rule \(\dfrac{a}{\sin A} = \dfrac{b}{\sin B} = \dfrac{c}{\sin C}\); cosine rule \(a^2 = b^2 + c^2 - 2bc\cos A\).

Example 4: In a triangle, \(a = 7\), \(b = 9\), and angle \(C = 50°\). Find \(c\).
\(c^2 = 7^2 + 9^2 - 2(7)(9)\cos 50°\). Using \(\cos 50° \approx 0.643\): \(c^2 \approx 130 - 81.0 = 49.0\), so \(c \approx 7.00\).

## Angles of elevation, depression, and bearings

Angle of elevation is measured upward from the horizontal; angle of depression downward. Bearings are always measured clockwise from North as a three-digit angle, e.g. due East is \(090°\) and due South-West is \(225°\).""",
        "related_topics": ["Geometry and Mensuration", "Algebraic Processes", "Sets and Binary Operations"],
    },
    {
        "subject": "Mathematics",
        "topic": "Geometry and Mensuration",
        "title": "Geometry and Mensuration",
        "summary": "Properties of shapes (angles, triangles, circles) and how to calculate their perimeter, area, and volume.",
        "glossary": [
            {"term": "Congruent", "definition": "shapes that are exactly the same size and shape"},
            {"term": "Similar", "definition": "shapes with the same shape but different size, with equal corresponding angles"},
            {"term": "Circle theorem", "definition": "a rule about angles and lines in a circle, e.g. the angle at the centre is twice the angle at the circumference"},
            {"term": "Perimeter", "definition": "the total distance around the outside of a shape"},
            {"term": "Surface area", "definition": "the total area covering the outside of a solid"},
        ],
        "content_md": r"""## Angles

Angles on a straight line sum to 180°; angles at a point sum to 360°; angles in a triangle sum to 180°; the sum of interior angles of a polygon with \(n\) sides is \((n-2)\times180°\).

Example 1: Find the sum of interior angles of a hexagon (6 sides).
\((6-2)\times180° = 4\times180° = 720°\).

## Pythagoras' theorem

In a right triangle, \(a^2 + b^2 = c^2\), where \(c\) is the hypotenuse (the longest side, opposite the right angle).

Example 2: A right triangle has legs 6cm and 8cm. Find the hypotenuse.
\(c = \sqrt{6^2+8^2} = \sqrt{36+64} = \sqrt{100} = 10\)cm.

## Circle theorems

Key ones JAMB tests: the angle at the centre is twice the angle at the circumference standing on the same arc; angles in the same segment are equal; the angle in a semicircle is 90°; opposite angles of a cyclic quadrilateral sum to 180°.

## Perimeter and area

- **Rectangle**: perimeter \(=2(l+w)\), area \(=l\times w\).
- **Triangle**: area \(=\dfrac{1}{2}\times\text{base}\times\text{height}\).
- **Circle**: circumference \(=2\pi r\), area \(=\pi r^2\).
- **Trapezium**: area \(=\dfrac{1}{2}(a+b)h\), where \(a,b\) are the parallel sides.

Example 3: Find the area of a circle with radius 7cm (use \(\pi \approx \dfrac{22}{7}\)).
Area \(= \dfrac{22}{7}\times7^2 = \dfrac{22}{7}\times49 = 154\)cm².

## Volume and surface area of solids

- **Cuboid**: volume \(=l\times w\times h\).
- **Cylinder**: volume \(=\pi r^2h\), curved surface area \(=2\pi rh\).
- **Cone**: volume \(=\dfrac{1}{3}\pi r^2h\).
- **Sphere**: volume \(=\dfrac{4}{3}\pi r^3\), surface area \(=4\pi r^2\).

Example 4: Find the volume of a cylinder with radius 3cm and height 10cm (use \(\pi\approx3.142\)).
Volume \(=3.142\times3^2\times10 = 3.142\times9\times10 = 282.78\)cm³.""",
        "related_topics": ["Coordinate Geometry and Trigonometry", "Sets and Binary Operations", "Number, Fractions, and Approximation"],
    },
    {
        "subject": "Mathematics",
        "topic": "Inequalities, Permutation, and Combination",
        "title": "Inequalities, Permutation, and Combination",
        "summary": "Solving inequalities, and counting arrangements (permutation) or selections (combination) without listing every possibility.",
        "glossary": [
            {"term": "Inequality", "definition": "a statement that one expression is greater than, less than, or not equal to another"},
            {"term": "Factorial (n!)", "definition": "the product of all positive integers up to n, e.g. \\(4! = 4\\times3\\times2\\times1=24\\)"},
            {"term": "Permutation", "definition": "an arrangement of items where order matters"},
            {"term": "Combination", "definition": "a selection of items where order does not matter"},
            {"term": "Sign flip", "definition": "when multiplying or dividing an inequality by a negative number, the inequality sign reverses"},
        ],
        "content_md": r"""## Linear inequalities

Solve a linear inequality exactly like an equation, but flip the inequality sign whenever you multiply or divide both sides by a negative number.

Example 1: Solve \(3 - 2x \le 9\).
Subtract 3: \(-2x \le 6\). Divide by \(-2\) (flip the sign): \(x \ge -3\).

## Quadratic inequalities

Rearrange to zero, factorize, find the critical values, then test which region satisfies the inequality.

Example 2: Solve \(x^2 - x - 6 > 0\).
Factorize: \((x-3)(x+2) > 0\). The critical values are \(x=3\) and \(x=-2\). Testing regions shows the product is positive when \(x < -2\) or \(x > 3\).

## Permutation

The number of ways to arrange \(r\) items chosen from \(n\), where order matters: \(nPr = \dfrac{n!}{(n-r)!}\).

Example 3: In how many ways can 3 people be arranged in a queue of 5?
\(5P3 = \dfrac{5!}{(5-3)!} = \dfrac{120}{2} = 60\).

## Combination

The number of ways to choose \(r\) items from \(n\), where order does not matter: \(nCr = \dfrac{n!}{r!(n-r)!}\).

Example 4: In how many ways can a committee of 3 be chosen from 8 people?
\(8C3 = \dfrac{8!}{3!\times5!} = \dfrac{8\times7\times6}{3\times2\times1} = 56\).

**Tip**: if the question involves arranging (order matters -- a queue, a password, a race finish), use permutation. If it involves selecting a group (order doesn't matter -- a committee, a team), use combination.""",
        "related_topics": ["Algebraic Processes", "Statistics and Probability", "Sets and Binary Operations"],
    },
    {
        "subject": "Mathematics",
        "topic": "Number, Fractions, and Approximation",
        "title": "Number, Fractions, and Approximation",
        "summary": "Working confidently with number bases, fractions, standard form, surds, and rounding -- the foundational number skills JAMB checks first.",
        "glossary": [
            {"term": "Standard form", "definition": "a number written as \\(A\\times10^n\\), where \\(1\\le A<10\\)"},
            {"term": "Surd", "definition": "an irrational root that cannot be simplified to a whole number, e.g. \\(\\sqrt{2}\\)"},
            {"term": "Significant figures", "definition": "the digits in a number that carry meaning for precision"},
            {"term": "Number base", "definition": "a system of counting using a fixed number of digits, e.g. base 2 (binary) uses only 0 and 1"},
            {"term": "Rationalize", "definition": "to remove a surd from the denominator of a fraction"},
        ],
        "content_md": r"""## Number bases

To convert from base 10 to another base, repeatedly divide by the new base and read the remainders bottom to top. To convert to base 10, multiply each digit by the base raised to its position power and add.

Example 1: Convert \(25_{10}\) to base 2.
\(25\div2=12\) remainder 1; \(12\div2=6\) remainder 0; \(6\div2=3\) remainder 0; \(3\div2=1\) remainder 1; \(1\div2=0\) remainder 1. Reading remainders bottom to top: \(25_{10} = 11001_2\).

## Standard form

Write a number as \(A \times 10^n\) with \(1 \le A < 10\).

Example 2: Write 0.00042 in standard form.
\(0.00042 = 4.2\times10^{-4}\).

## Approximation

Decimal places count digits after the decimal point; significant figures count all meaningful digits starting from the first non-zero digit.

Example 3: Round 3.14159 to 3 significant figures.
The first 3 significant digits are 3, 1, 4; the next digit (1) doesn't round up, so the answer is 3.14.

## Surds

Simplify by pulling out perfect square factors; rationalize a denominator by multiplying top and bottom by a matching surd.

Example 4: Simplify \(\sqrt{50}\).
\(\sqrt{50} = \sqrt{25\times2} = 5\sqrt{2}\).

Example 5: Rationalize \(\dfrac{1}{\sqrt{3}}\).
Multiply top and bottom by \(\sqrt{3}\): \(\dfrac{1}{\sqrt{3}}\times\dfrac{\sqrt{3}}{\sqrt{3}} = \dfrac{\sqrt{3}}{3}\).

## Indices (laws of exponents)

- \(a^m \times a^n = a^{m+n}\)
- \(a^m \div a^n = a^{m-n}\)
- \((a^m)^n = a^{mn}\)
- \(a^0 = 1\), \(a^{-n} = \dfrac{1}{a^n}\)

Example 6: Simplify \(\dfrac{2^5 \times 2^3}{2^4}\).
\(= 2^{5+3-4} = 2^4 = 16\).""",
        "related_topics": ["Algebraic Processes", "Sequences, Series, and Variation", "Commercial Arithmetic"],
    },
    {
        "subject": "Mathematics",
        "topic": "Sequences, Series, and Variation",
        "title": "Sequences, Series, and Variation",
        "summary": "Patterns in number sequences (arithmetic and geometric progressions) and how one quantity varies with another.",
        "glossary": [
            {"term": "Arithmetic progression (AP)", "definition": "a sequence with a constant difference between consecutive terms"},
            {"term": "Geometric progression (GP)", "definition": "a sequence with a constant ratio between consecutive terms"},
            {"term": "Common difference", "definition": "the fixed amount added to get the next term in an AP"},
            {"term": "Common ratio", "definition": "the fixed number multiplied to get the next term in a GP"},
            {"term": "Direct variation", "definition": "when one quantity increases as another increases, in constant proportion (\\(y=kx\\))"},
        ],
        "content_md": r"""## Arithmetic progression (AP)

nth term: \(T_n = a + (n-1)d\), where \(a\) is the first term and \(d\) is the common difference.
Sum of n terms: \(S_n = \dfrac{n}{2}[2a+(n-1)d]\).

Example 1: Find the 10th term of the AP \(3, 7, 11, 15, \dots\)
Here \(a=3, d=4\). \(T_{10} = 3+(10-1)(4) = 3+36 = 39\).

Example 2: Find the sum of the first 15 terms of the same AP.
\(S_{15} = \dfrac{15}{2}[2(3)+(15-1)(4)] = 7.5[6+56] = 7.5\times62 = 465\).

## Geometric progression (GP)

nth term: \(T_n = ar^{n-1}\), where \(r\) is the common ratio.
Sum of n terms: \(S_n = \dfrac{a(r^n-1)}{r-1}\) (for \(r\ne1\)).
Sum to infinity (only when \(-1<r<1\)): \(S_\infty = \dfrac{a}{1-r}\).

Example 3: Find the 6th term of the GP \(2, 6, 18, 54, \dots\)
Here \(a=2, r=3\). \(T_6 = 2\times3^{6-1} = 2\times243 = 486\).

Example 4: Find the sum to infinity of \(8, 4, 2, 1, \dots\)
Here \(a=8, r=\dfrac{1}{2}\). \(S_\infty = \dfrac{8}{1-0.5} = \dfrac{8}{0.5} = 16\).

## Variation

- **Direct variation**: \(y = kx\) (y increases as x increases).
- **Inverse variation**: \(y = \dfrac{k}{x}\) (y decreases as x increases).
- **Joint variation**: \(y = kxz\) (y depends on two variables together).

Example 5: \(y\) varies directly as \(x\). When \(x=5\), \(y=20\). Find \(y\) when \(x=8\).
Find \(k\): \(20 = k(5)\), so \(k=4\). Then \(y = 4(8) = 32\).""",
        "related_topics": ["Algebraic Processes", "Number, Fractions, and Approximation", "Commercial Arithmetic"],
    },
    {
        "subject": "Mathematics",
        "topic": "Sets and Binary Operations",
        "title": "Sets and Binary Operations",
        "summary": "Describing and combining collections of objects with set notation and Venn diagrams, and the rules that govern custom-defined operations.",
        "glossary": [
            {"term": "Set", "definition": "a well-defined collection of distinct objects"},
            {"term": "Union (∪)", "definition": "all elements in either set (or both)"},
            {"term": "Intersection (∩)", "definition": "elements common to both sets"},
            {"term": "Complement", "definition": "elements not in the set, from the universal set"},
            {"term": "Closure", "definition": "a set is closed under an operation if combining any two members gives a result still in the set"},
        ],
        "content_md": r"""## Set notation and Venn diagrams

\(A \cup B\) means everything in A or B (or both). \(A \cap B\) means only what's in both. \(A'\) (complement) means everything NOT in A, from the universal set \(U\). \(n(A)\) means the number of elements in A.

Example 1: If \(U=\{1,2,\dots,10\}\), \(A=\{2,4,6,8,10\}\), \(B=\{1,2,3,4,5\}\), find \(A\cap B\) and \(A\cup B\).
\(A\cap B = \{2,4\}\). \(A\cup B = \{1,2,3,4,5,6,8,10\}\).

## Two-set word problems

The key formula: \(n(A\cup B) = n(A) + n(B) - n(A\cap B)\).

Example 2: In a class of 40 students, 25 like Mathematics, 20 like English, and 10 like both. How many like neither?
\(n(M\cup E) = 25+20-10 = 35\). Students who like neither \(= 40-35 = 5\).

## Three-set problems

Draw a Venn diagram with three overlapping circles and fill in from the centre (the "all three" region) outward, subtracting as you go so you don't double-count.

## Binary operations

A binary operation \(*\) combines two elements of a set to give another element. To evaluate \(a * b\), substitute into the given rule or table.

Example 3: If \(a * b = a^2 + b - ab\), find \(3 * 2\).
\(3*2 = 3^2 + 2 - (3\times2) = 9+2-6 = 5\).

Key properties to check for a binary operation:

- **Closure**: does \(a*b\) always stay in the same set?
- **Commutative**: is \(a*b = b*a\) for all a, b?
- **Associative**: is \((a*b)*c = a*(b*c)\)?
- **Identity element** \(e\): a value where \(a*e = e*a = a\).

Example 4: For \(a*b = a+b-1\), find the identity element.
Set \(a*e=a\): \(a+e-1=a\), so \(e=1\).""",
        "related_topics": ["Coordinate Geometry and Trigonometry", "Statistics and Probability", "Inequalities, Permutation, and Combination"],
    },
    {
        "subject": "Mathematics",
        "topic": "Statistics and Probability",
        "title": "Statistics and Probability",
        "summary": "Summarizing data with averages and spread, and calculating the likelihood of events.",
        "glossary": [
            {"term": "Mean", "definition": "the average -- sum of values divided by how many there are"},
            {"term": "Median", "definition": "the middle value when data is arranged in order"},
            {"term": "Mode", "definition": "the value that appears most often"},
            {"term": "Probability", "definition": "a measure between 0 and 1 of how likely an event is, \\(P(E)=\\dfrac{\\text{favourable outcomes}}{\\text{total outcomes}}\\)"},
            {"term": "Mutually exclusive events", "definition": "events that cannot happen at the same time"},
        ],
        "content_md": r"""## Mean, median, and mode

Mean \(=\dfrac{\text{sum of values}}{\text{number of values}}\). Median is the middle value once data is ordered (average the two middle values if there's an even count). Mode is the most frequent value.

Example 1: Find the mean, median, and mode of \(4, 8, 6, 8, 3, 9, 8\).
Mean \(= \dfrac{4+8+6+8+3+9+8}{7} = \dfrac{46}{7} \approx 6.57\). Ordered: \(3,4,6,8,8,8,9\) -- median is the 4th value, 8. Mode is 8 (appears 3 times).

## Grouped data

For grouped/frequency data, use the midpoint of each class interval as a representative value: mean \(=\dfrac{\sum fx}{\sum f}\), where \(f\) is frequency and \(x\) is the class midpoint.

Example 2: A class scored: 1-3 (freq 2), 4-6 (freq 5), 7-9 (freq 3). Find the mean.
Midpoints: 2, 5, 8. \(\sum fx = 2(2)+5(5)+3(8) = 4+25+24=53\). \(\sum f = 10\). Mean \(=53/10=5.3\).

## Range and spread

Range \(=\) highest value \(-\) lowest value -- the simplest measure of spread.

## Basic probability

\(P(E) = \dfrac{\text{number of favourable outcomes}}{\text{total possible outcomes}}\). Probability is always between 0 (impossible) and 1 (certain).

Example 3: A bag has 5 red and 3 blue balls. Find the probability of picking a red ball.
\(P(\text{red}) = \dfrac{5}{5+3} = \dfrac{5}{8}\).

## Combined events

- **Mutually exclusive** (can't both happen): \(P(A \text{ or } B) = P(A)+P(B)\).
- **Independent** (one doesn't affect the other): \(P(A \text{ and } B) = P(A)\times P(B)\).

Example 4: A die is rolled once. Find the probability of getting a 2 or a 5.
These are mutually exclusive: \(P(2\text{ or }5) = \dfrac{1}{6}+\dfrac{1}{6} = \dfrac{2}{6} = \dfrac{1}{3}\).

Example 5: A coin is tossed and a die is rolled. Find the probability of getting heads AND a 6.
These are independent: \(P(\text{heads and }6) = \dfrac{1}{2}\times\dfrac{1}{6} = \dfrac{1}{12}\).""",
        "related_topics": ["Inequalities, Permutation, and Combination", "Number, Fractions, and Approximation", "Commercial Arithmetic"],
    },
    {
        "subject": "English",
        "topic": "Reading Comprehension",
        "title": "Reading Comprehension",
        "summary": "How to read a passage fast and answer literal, inferential, vocabulary, and tone questions accurately -- without re-reading the whole passage for every question.",
        "glossary": [
            {"term": "Skimming", "definition": "reading quickly to get the general idea of a passage, not every word"},
            {"term": "Scanning", "definition": "moving your eyes over a passage to locate one specific fact or word"},
            {"term": "Inference", "definition": "a conclusion the passage strongly implies but never states outright"},
            {"term": "Context clue", "definition": "the surrounding words that tell you what an unfamiliar word means in that sentence"},
            {"term": "Tone", "definition": "the author's attitude towards the subject -- e.g. critical, admiring, sarcastic, neutral"},
            {"term": "Main idea", "definition": "the single point the whole passage is built around, as opposed to a supporting detail"},
        ],
        "content_md": r"""## What comprehension passages test

Every JAMB comprehension passage is followed by a mix of question types: literal (the answer is stated directly), inferential (the answer is implied, not written), vocabulary-in-context, tone/attitude, and main idea/title. Knowing which type you're facing tells you where to look for the answer.

## Read the questions first

Before reading the passage itself, skim the questions (not the options). This tells you what to hunt for, so your first read of the passage is already purposeful instead of passive.

## The two-pass approach

First pass: read the whole passage at normal speed for the general idea -- don't stop for words you don't know. Second pass: go question by question, scanning back to the relevant part of the passage to confirm your answer. Never answer from memory alone; always verify against the text.

## Literal questions

These ask for a fact stated directly in the passage. Scan for keywords from the question -- names, numbers, dates -- and read the sentence around that keyword carefully.

Example 1: A passage states "The festival, first held in 1962, now attracts over ten thousand visitors annually." A question asks when the festival began.
Scan for the number and read its sentence: the passage states 1962 directly, so that is the literal answer -- no interpretation needed.

## Inferential questions

These ask what the passage suggests without saying it outright. Look for word choices, contrasts, or cause-and-effect language that point to an unstated conclusion.

Example 2: A passage describes a trader who "counted his coins twice before locking the shop, then walked home by the longer, well-lit road." A question asks what this suggests about the trader.
Nothing states he is careful or cautious, but counting money twice and choosing a longer, well-lit route over a shorter one both imply caution -- that is the inference, built from two small details rather than one stated fact.

## Vocabulary-in-context questions

These ask what a word means as used in the passage -- not its general dictionary meaning. A word like "sound" can mean "healthy," "make noise," or "reasonable" depending on context; always re-read the full sentence, not just the word.

Example 3: "Her argument was sound, backed by three independent studies." A question asks what "sound" means here.
The sentence is about an argument backed by evidence, not about noise or health -- so "sound" here means valid/well-founded, not any of its other common meanings.

## Tone and the author's attitude

Tone questions ask how the author feels about the subject, shown through word choice rather than direct statement. Common tone words tested: critical, admiring, sarcastic, nostalgic, objective/neutral, sympathetic, mocking. Words like "sadly," "unfortunately," "remarkably," or "predictably" are strong tone signals -- watch for them.

## Main idea and title questions

The main idea is usually built or confirmed in the first and last paragraphs -- the opening introduces the topic, the closing often restates or sums it up. A wrong option for a "best title" question is usually too narrow (only covers one paragraph) or too broad (covers more than the passage discusses).

Example 4: A passage spends one paragraph each on causes of soil erosion, its effects on farming, and government prevention efforts. A question asks for the best title.
An option naming only "Causes of Soil Erosion" is too narrow -- it ignores two of the three paragraphs. The best title covers all three: something like "Soil Erosion: Causes, Effects, and Prevention."

## Common traps to avoid

Options containing absolute words like "always," "never," or "completely" are often wrong, because passages rarely make such strong claims. An option can also be true in real life but still wrong if the passage itself never says it -- always check the text, not your outside knowledge.""",
        "related_topics": ["Lexis and Structure", "Cloze Test"],
    },
    {
        "subject": "English",
        "topic": "Lexis and Structure",
        "title": "Lexis and Structure",
        "summary": "The grammar and vocabulary rules JAMB tests most: synonyms/antonyms, idioms, concord, tense, prepositions, and sentence transformation (active/passive, direct/indirect speech).",
        "glossary": [
            {"term": "Concord", "definition": "subject-verb agreement -- a singular subject takes a singular verb, a plural subject takes a plural verb"},
            {"term": "Synonym", "definition": "a word with the same or nearly the same meaning as another"},
            {"term": "Antonym", "definition": "a word with the opposite meaning to another"},
            {"term": "Idiom", "definition": "a fixed expression whose meaning can't be worked out from its individual words, e.g. \"spill the beans\""},
            {"term": "Active voice", "definition": "the subject performs the action, e.g. \"The boy kicked the ball\""},
            {"term": "Passive voice", "definition": "the subject receives the action, e.g. \"The ball was kicked by the boy\""},
            {"term": "Reported (indirect) speech", "definition": "retelling what someone said without quoting their exact words"},
        ],
        "content_md": r"""## Synonyms and antonyms

JAMB tests both directly ("choose the word closest in meaning to...") and inside sentences ("choose the word that best replaces the underlined word"). Learn words in groups, not isolation -- e.g. happy/glad/elated/jubilant (increasing intensity) is more useful than memorising single pairs.

Example 1: Choose the word closest in meaning to "meticulous" as used in "She was meticulous in her record-keeping."
Meticulous describes extreme, careful attention to detail -- the closest synonym among typical options is "thorough," not "quick" or "careless" (which is actually its antonym).

## Idiomatic expressions

Idioms cannot be translated word-for-word. Learn the whole phrase and its real meaning together.

Example 2: "The manager decided to turn a blind eye to the latecomers." What does the idiom mean?
"Turn a blind eye" means to deliberately ignore something you've noticed -- not a literal statement about eyesight.

## Concord (subject-verb agreement)

- A singular subject takes a singular verb: "The student writes every day."
- A plural subject takes a plural verb: "The students write every day."
- Subjects joined by "and" are usually plural: "Musa and Ada are here."
- Subjects joined by "or"/"nor" agree with the nearer subject: "Neither the teacher nor the students were ready."
- Collective nouns (team, family, government) usually take a singular verb when acting as one unit: "The team is winning."
- Indefinite pronouns like "everyone," "everybody," "each," and "nobody" are always singular: "Everyone is present."

Example 3: Choose the correct option: "Neither of the answers ___ correct."
"Neither" is singular even though it refers to two things, so the verb must be singular: "is correct," not "are correct."

## Tense and aspect

Tense errors are one of the most common JAMB traps -- especially mixing past and present within one sentence, and misusing the present perfect (have/has + past participle) for an action still linked to now.

Example 4: Choose the correct option: "By the time we arrived, the meeting ___ already ___."
This describes one past action completed before another past action, which needs the past perfect: "had already started," not "has already started" or "already starts."

## Prepositions

Many JAMB errors involve prepositions fixed to particular words (collocations) rather than logic -- these must be memorised: "married to" (not "with"), "different from" (not "than," in formal English), "responsible for," "capable of," "interested in," "arrive at/in" (not "arrive to").

Example 5: Choose the correct option: "He is very good ___ mathematics."
"Good at" is the fixed collocation -- "good in" or "good on" are not standard here.

## Active and passive voice

To change active to passive: move the object of the active sentence to the front, add a form of "be" + past participle, and (optionally) add "by + the original subject."

Example 6: Change to passive voice: "The committee approved the budget."
The object "the budget" moves to the front: "The budget was approved by the committee."

## Direct and indirect (reported) speech

When reporting speech, tenses usually shift one step back (present becomes past, past becomes past perfect), and pronouns/time words change to fit the new speaker's perspective ("today" becomes "that day," "tomorrow" becomes "the next day").

Example 7: Change to indirect speech: Ada said, "I am tired today."
The present tense shifts back and "today" changes: Ada said that she was tired that day.

## Sentence types

- **Simple sentence**: one independent clause, e.g. "The rain stopped."
- **Compound sentence**: two independent clauses joined by "and," "but," "or," or a semicolon, e.g. "The rain stopped, and the sun came out."
- **Complex sentence**: an independent clause plus a dependent clause introduced by a word like "because," "although," "when," or "since" -- e.g. "The match was cancelled because the rain did not stop." """,
        "related_topics": ["Reading Comprehension", "Cloze Test"],
    },
    {
        "subject": "English",
        "topic": "Cloze Test",
        "title": "Cloze Test",
        "summary": "A worked approach to filling numbered blanks in a passage using grammar, meaning, and collocation clues from the surrounding sentences.",
        "glossary": [
            {"term": "Cloze test", "definition": "a passage with words removed and replaced by numbered blanks, which you fill by choosing the best option for each"},
            {"term": "Collocation", "definition": "words that habitually go together, e.g. \"heavy rain\" rather than \"strong rain\""},
            {"term": "Cohesion", "definition": "how sentences in a passage connect logically and grammatically to each other"},
        ],
        "content_md": r"""## What a cloze test is

A cloze passage removes roughly 10-15 words and replaces each with a numbered blank. For each blank you're given four option words, and only one fits both the grammar and the meaning of that exact spot -- not just any word that could plausibly fit an isolated sentence.

## Read the whole passage first

Never fill blanks as you meet them on a first read. Read the entire passage once, ignoring the blanks, to understand the overall topic and tone. This context often makes an otherwise-tricky blank obvious, because you already know what the passage is generally about.

## Using the words before and after the blank

The words immediately surrounding a blank usually narrow it down more than the whole passage does. Check what part of speech is needed (noun, verb, adjective, preposition) and whether the sentence needs a word that matches the tense and number of nearby verbs and subjects.

Example 1: "The farmers work hard every season, but the ___ rains this year destroyed most of the crop." Options: (a) heavy (b) strong (c) hard (d) big
The blank describes rain, and "rain" collocates specifically with "heavy" in standard English -- "strong rain" and "hard rain" are not the natural pairing JAMB expects, even though they might sound almost plausible in isolation.

## Watching for collocations

Certain words are almost always paired with specific partners: "make a decision" (not "do a decision"), "heavy traffic," "strictly forbidden," "deeply concerned," "highly unlikely." When a blank sits next to a strong collocate, that partner word usually decides the answer.

Example 2: "The government has ___ forbidden the importation of the banned chemical." Options: (a) strictly (b) hardly (c) rarely (d) barely
"Strictly forbidden" is the standard collocation for an absolute ban -- the passage's meaning (a firm prohibition) also rules out "hardly," "rarely," and "barely," which all weaken the statement instead of strengthening it.

## Keeping tense and grammar consistent

A cloze passage is usually written in one consistent tense throughout. If the surrounding sentences are in the past tense, the correct option for a verb blank must also be in the past tense, even if another option is a "more common" word.

Example 3: "Yesteryear, farming ___ the major occupation of the villagers before the discovery of oil." Options: (a) was (b) is (c) has been (d) will be
The passage marker "yesteryear" together with "before the discovery of oil" fixes this firmly in the past, so only the simple past "was" is grammatically consistent with the rest of the sentence.""",
        "related_topics": ["Lexis and Structure", "Reading Comprehension"],
    },
    {
        "subject": "English",
        "topic": "Oral English",
        "title": "Oral English",
        "summary": "Vowel and consonant sounds, silent letters, word stress, and rhymes -- tested by asking which word shares (or differs from) the sound of an underlined letter, or which syllable carries the stress.",
        "glossary": [
            {"term": "Vowel sound", "definition": "a speech sound made with an open vocal tract and no blockage of airflow, e.g. the sounds in \"cat,\" \"see,\" \"go\""},
            {"term": "Consonant sound", "definition": "a speech sound made by partly or fully blocking the airflow, e.g. \"b,\" \"t,\" \"sh\""},
            {"term": "Diphthong", "definition": "a single syllable where the tongue glides from one vowel sound to another, e.g. the \"oy\" in \"boy\""},
            {"term": "Monophthong", "definition": "a single, unchanging vowel sound, e.g. the \"ee\" in \"see\""},
            {"term": "Stress", "definition": "the syllable in a word pronounced with more force and a clearer vowel than the others"},
            {"term": "Silent letter", "definition": "a letter written in a word but not pronounced, e.g. the \"b\" in \"comb\""},
            {"term": "Homophone", "definition": "words that sound identical but differ in spelling and meaning, e.g. \"flower\" and \"flour\""},
        ],
        "content_md": r"""## Vowel sounds

English has more vowel sounds than vowel letters, so the same letter can be pronounced differently in different words, and different letters can share the same sound. Short vowel sounds include those in "bit," "bet," "cat," "cut," "hot," and "put." Long vowel sounds include those in "see," "car," "saw," "too," and "her." JAMB questions usually give an underlined letter in a keyword and ask which option word has the same (or a different) vowel sound.

Example 1: Which word has the same vowel sound as the underlined letter in "s__ea__t" (seat)? Options: (a) bread (b) neat (c) great (d) head
"Seat" uses the long "ee" sound. Of the options, only "neat" shares that exact sound -- "bread" and "head" use the short "e" sound, and "great" uses a completely different vowel sound (like "ay").

## Diphthongs

A diphthong is one syllable where the sound glides between two vowel positions, common examples being the sounds in "day," "my," "boy," "how," "go," "here," "there," and "sure." These are frequently confused with monophthongs (single, steady vowel sounds) in exam questions.

Example 2: Which word has a different vowel sound from the others? Options: (a) toy (b) boil (c) coin (d) food
"Toy," "boil," and "coin" all share the same gliding "oy" diphthong. "Food" uses a long, steady monophthong instead, making it the odd one out.

## Consonant sounds

Consonants come in voiced/voiceless pairs made the same way in the mouth, differing only in whether the vocal cords vibrate: /p/-/b/, /t/-/d/, /k/-/g/, /f/-/v/, /s/-/z/. Letter combinations can also represent a single consonant sound, such as "sh" in "ship," "ch" in "chair," "th" in "think" (voiceless) versus "th" in "this" (voiced), and "ng" in "sing."

Example 3: Which word has the same consonant sound as the underlined letters in "thi__n__k"? Options: (a) this (b) that (c) three (d) then
"Think" uses the voiceless "th" sound (no vocal cord vibration). "Three" shares that same voiceless sound, while "this," "that," and "then" all use the voiced "th" instead.

## Silent letters

Many English words keep a letter in spelling that is no longer pronounced. Common patterns: "b" after "m" at a word's end (comb, climb, thumb), "k" before "n" at a word's start (know, knee, knife), "l" in some words with "al" or "ol" (half, walk, talk, calm), "w" before "r" (write, wrong, wrap), and silent "h" in some words (hour, honest, honour).

Example 4: Which letter is silent in "psychology"?
The "p" at the start is silent -- the word is pronounced starting with the "s" sound, a pattern shared by other Greek-derived words like "pneumonia" and "psalm."

## Word and sentence stress

Many two-syllable English words change meaning depending on which syllable is stressed -- typically the first syllable for a noun and the second for the related verb: 'CONtent (satisfied, or as a noun meaning "what's inside") versus con'TENT is not how this pair works, but classic exam examples include 'PROduce (the noun, meaning farm goods) versus pro'DUCE (the verb, meaning to make), and 'REcord (the noun) versus re'CORD (the verb).

Example 5: Which syllable is stressed in "record" when it is used as a verb, as in "Please record the meeting"?
As a verb, the stress falls on the second syllable: re'CORD. When the same word is a noun ("I have a record of the meeting"), the stress shifts to the first syllable: 'REcord.

## Rhymes and homophones

Rhyme questions ask which word ends with the same sound as a given word -- judged by sound, not spelling, so "though" rhymes with "go" despite looking very different. Homophone questions test words that sound identical but are spelled differently and mean different things, such as "flower"/"flour," "wait"/"weight," and "there"/"their"/"they're."

Example 6: Which word rhymes with "cough"? Options: (a) rough (b) though (c) bough (d) enough
Despite all four words ending in "-ough," they are pronounced differently. "Cough" rhymes with "off." Among the options, "rough" and "enough" rhyme with each other (ending in an "-uff" sound) but not with "cough" -- and neither do "though" (rhymes with "go") or "bough" (rhymes with "cow"). In practice, JAMB's correct answer for this classic set depends on the exact option list given, which is why this topic rewards learning specific word groups rather than guessing from spelling alone.""",
        "related_topics": ["Lexis and Structure", "Reading Comprehension"],
    },
    {
        "subject": "Physics",
        "topic": "Electricity and Magnetism",
        "title": "Electricity and Magnetism",
        "summary": "Ohm's law, series and parallel circuits, electrical power, and the basics of magnetism and electromagnetic induction.",
        "glossary": [
            {"term": "Current", "definition": "the rate of flow of electric charge, measured in amperes (A)"},
            {"term": "Potential difference (voltage)", "definition": "the energy transferred per unit charge between two points, measured in volts (V)"},
            {"term": "Resistance", "definition": "how strongly a component opposes current flow, measured in ohms (\\(\\Omega\\))"},
            {"term": "Electromotive force (EMF)", "definition": "the energy a source (like a battery) gives to each unit of charge it pushes round a circuit"},
            {"term": "Magnetic flux", "definition": "a measure of the total magnetic field passing through a given area"},
            {"term": "Electromagnetic induction", "definition": "producing an EMF (and current) by changing the magnetic flux through a circuit"},
        ],
        "content_md": r"""## Ohm's law and resistor networks

Ohm's law: \(V = IR\), where \(V\) is potential difference, \(I\) is current, and \(R\) is resistance. In series, the same current flows through every component and resistances simply add: \(R_{total} = R_1 + R_2 + \dots\). In parallel, every branch has the same voltage across it and resistances combine as \(\dfrac{1}{R_{total}} = \dfrac{1}{R_1} + \dfrac{1}{R_2} + \dots\)

Example 1: A 4 Ω and a 6 Ω resistor are connected in series across a 20 V battery. Find the current flowing.
\(R_{total} = 4 + 6 = 10\,\Omega\). \(I = \dfrac{V}{R} = \dfrac{20}{10} = 2\,A\).

Example 2: A 3 Ω and a 6 Ω resistor are connected in parallel. Find the combined resistance.
\(\dfrac{1}{R} = \dfrac{1}{3} + \dfrac{1}{6} = \dfrac{2}{6} + \dfrac{1}{6} = \dfrac{3}{6}\), so \(R = 2\,\Omega\).

## Electrical power and energy

Power delivered to a component: \(P = VI = I^2R = \dfrac{V^2}{R}\). Energy transferred over time \(t\): \(E = Pt\).

Example 3: Find the power dissipated in a 5 Ω resistor carrying a current of 2 A.
\(P = I^2R = 2^2 \times 5 = 20\,W\).

## Electrostatics

Like charges repel, unlike charges attract. Coulomb's law gives the force between two point charges: \(F = \dfrac{kQ_1Q_2}{r^2}\), which decreases sharply as the distance \(r\) increases. A charged rod can attract small, light, uncharged objects (like bits of paper) by inducing an opposite charge on the near side of the object -- this is induction, and doesn't require actual contact or charge transfer.

## Magnetism and electromagnetic induction

A current-carrying wire creates a circular magnetic field around itself; the right-hand grip rule (thumb points along the current, fingers curl in the field's direction) gives the field's direction. Electromagnetic induction is the reverse idea: moving a magnet relative to a coil, or otherwise changing the magnetic flux through a circuit, induces an EMF and drives a current. Lenz's law says the induced current always flows in the direction that opposes the change causing it -- this is why you feel resistance pushing a magnet into a coil connected in a loop.

Example 4: A bar magnet's north pole is pushed into a coil connected to a closed circuit. What can you say about the induced current's direction?
By Lenz's law, the induced current opposes the increasing flux from the approaching north pole -- so the coil's near face acts like a north pole too (repelling the magnet), which fixes the current's direction via the right-hand rule applied to that face.""",
        "related_topics": ["Electronics and Alternating Current", "General Physics and Measurement"],
    },
    {
        "subject": "Physics",
        "topic": "Waves, Sound, and Optics",
        "title": "Waves, Sound, and Optics",
        "summary": "The wave equation, sound and echoes, and reflection/refraction of light through mirrors and lenses.",
        "glossary": [
            {"term": "Wavelength", "definition": "the distance between two consecutive identical points on a wave (e.g. crest to crest), symbol \\(\\lambda\\)"},
            {"term": "Frequency", "definition": "the number of complete waves passing a point per second, measured in hertz (Hz)"},
            {"term": "Amplitude", "definition": "the maximum displacement of a wave from its rest position"},
            {"term": "Refraction", "definition": "the bending of a wave (e.g. light) as it passes from one medium into another"},
            {"term": "Refractive index", "definition": "a measure of how much a medium bends light, \\(n = \\dfrac{\\sin i}{\\sin r}\\)"},
            {"term": "Total internal reflection", "definition": "when light travelling in a denser medium hits a boundary at an angle greater than the critical angle and reflects entirely back in"},
        ],
        "content_md": r"""## The wave equation

Every wave obeys \(v = f\lambda\), linking speed, frequency, and wavelength. Increasing frequency while speed stays fixed (as in a single medium) means wavelength must shrink to compensate.

Example 1: A wave has a frequency of 50 Hz and a wavelength of 4 m. Find its speed.
\(v = f\lambda = 50 \times 4 = 200\,m/s\).

## Sound and echoes

Sound is a mechanical wave that needs a medium to travel through. An echo is a reflected sound wave; since the sound travels to the reflecting surface and back, the distance to that surface is \(d = \dfrac{vt}{2}\), where \(t\) is the total time from emission to hearing the echo.

Example 2: An echo is heard 0.5 s after a sound is emitted, and the speed of sound in air is 340 m/s. Find the distance to the reflecting surface.
\(d = \dfrac{vt}{2} = \dfrac{340 \times 0.5}{2} = 85\,m\).

## Reflection and refraction of light

The law of reflection says the angle of incidence equals the angle of reflection. Refraction is the bending of light as it crosses into a different medium, governed by Snell's law: \(n = \dfrac{\sin i}{\sin r}\), where \(i\) is the angle of incidence and \(r\) is the angle of refraction, both measured from the normal.

Example 3: Light passes from air into glass (\(n = 1.5\)) at an angle of incidence of 30°. Find the angle of refraction.
\(\sin r = \dfrac{\sin i}{n} = \dfrac{\sin 30}{1.5} = \dfrac{0.5}{1.5} = 0.333\), so \(r = \sin^{-1}(0.333) \approx 19.5°\).

## Mirrors and lenses

The mirror/lens formula relates object distance \(u\), image distance \(v\), and focal length \(f\): \(\dfrac{1}{f} = \dfrac{1}{u} + \dfrac{1}{v}\). Magnification is \(m = \dfrac{v}{u}\).

Example 4: An object is placed 30 cm from a converging lens of focal length 10 cm. Find the image distance.
\(\dfrac{1}{10} = \dfrac{1}{30} + \dfrac{1}{v}\), so \(\dfrac{1}{v} = \dfrac{1}{10} - \dfrac{1}{30} = \dfrac{2}{30}\), giving \(v = 15\,cm\).

## Total internal reflection

This happens only when light travels from a denser medium towards a less dense one, at an angle beyond the critical angle \(C\), where \(\sin C = \dfrac{1}{n}\).

Example 5: Find the critical angle for glass with refractive index 1.5.
\(\sin C = \dfrac{1}{1.5} = 0.667\), so \(C = \sin^{-1}(0.667) \approx 41.8°\).""",
        "related_topics": ["General Physics and Measurement", "Electricity and Magnetism"],
    },
    {
        "subject": "Physics",
        "topic": "Mechanics, Motion, and Energy",
        "title": "Mechanics, Motion, and Energy",
        "summary": "The equations of motion, Newton's laws, momentum conservation, and work, energy, and power.",
        "glossary": [
            {"term": "Velocity", "definition": "the rate of change of displacement -- speed in a given direction"},
            {"term": "Acceleration", "definition": "the rate of change of velocity"},
            {"term": "Momentum", "definition": "the product of an object's mass and velocity, \\(p = mv\\)"},
            {"term": "Newton's second law", "definition": "the resultant force on an object equals its mass times its acceleration, \\(F = ma\\)"},
            {"term": "Work", "definition": "energy transferred when a force moves its point of application through a distance, \\(W = Fd\\)"},
            {"term": "Kinetic energy", "definition": "the energy an object has due to its motion, \\(KE = \\dfrac{1}{2}mv^2\\)"},
        ],
        "content_md": r"""## Equations of motion (SUVAT)

For constant acceleration, three equations connect initial velocity \(u\), final velocity \(v\), acceleration \(a\), displacement \(s\), and time \(t\): \(v = u + at\), \(s = ut + \dfrac{1}{2}at^2\), and \(v^2 = u^2 + 2as\).

Example 1: A car accelerates uniformly from rest to 20 m/s in 5 s. Find its acceleration and the distance it covers.
\(a = \dfrac{v-u}{t} = \dfrac{20-0}{5} = 4\,m/s^2\). \(s = ut + \dfrac{1}{2}at^2 = 0 + \dfrac{1}{2}(4)(25) = 50\,m\).

## Newton's laws of motion

Newton's first law: an object stays at rest or moving at constant velocity unless acted on by a resultant force. Newton's second law: \(F = ma\). Newton's third law: every action has an equal and opposite reaction.

Example 2: A resultant force of 15 N acts on a mass of 3 kg. Find its acceleration.
\(a = \dfrac{F}{m} = \dfrac{15}{3} = 5\,m/s^2\).

## Momentum and its conservation

Momentum \(p = mv\). In any collision or explosion with no external force, total momentum before equals total momentum after.

Example 3: A 2 kg object moving at 5 m/s collides with, and sticks to, a stationary 3 kg object. Find their common velocity after the collision.
Momentum before \(= 2 \times 5 = 10\,kg\,m/s\). This equals momentum after: \((2+3)v = 10\), so \(v = 2\,m/s\).

## Work, energy, and power

Work \(W = Fd\) (force in the direction of motion). Kinetic energy \(KE = \dfrac{1}{2}mv^2\); gravitational potential energy \(PE = mgh\). Power is the rate of doing work: \(P = \dfrac{W}{t}\).

Example 4: Find the kinetic energy of a 4 kg object moving at 3 m/s, and the potential energy of a 2 kg object raised 5 m (take \(g = 10\,m/s^2\)).
\(KE = \dfrac{1}{2}(4)(3^2) = 18\,J\). \(PE = mgh = 2 \times 10 \times 5 = 100\,J\).""",
        "related_topics": ["Properties of Matter and Fluids", "General Physics and Measurement"],
    },
    {
        "subject": "Physics",
        "topic": "Heat and Thermodynamics",
        "title": "Heat and Thermodynamics",
        "summary": "Specific heat capacity, latent heat, and the gas laws that describe how gases respond to changes in pressure, volume, and temperature.",
        "glossary": [
            {"term": "Specific heat capacity", "definition": "the heat energy needed to raise the temperature of 1 kg of a substance by 1°C"},
            {"term": "Latent heat", "definition": "the heat energy absorbed or released during a change of state, at constant temperature"},
            {"term": "Absolute zero", "definition": "the lowest possible temperature, 0 K or -273°C, where particles have minimum kinetic energy"},
            {"term": "Boyle's law", "definition": "at constant temperature, the pressure and volume of a fixed mass of gas are inversely related: \\(P_1V_1 = P_2V_2\\)"},
            {"term": "Charles' law", "definition": "at constant pressure, the volume of a fixed mass of gas is directly proportional to its absolute temperature"},
        ],
        "content_md": r"""## Heating without changing state

The heat energy needed to change a substance's temperature is \(Q = mc\Delta T\), where \(c\) is the specific heat capacity and \(\Delta T\) is the temperature change.

Example 1: Find the heat needed to raise the temperature of 2 kg of water from 20°C to 80°C (specific heat capacity of water = 4200 J/kg°C).
\(Q = mc\Delta T = 2 \times 4200 \times 60 = 504{,}000\,J = 504\,kJ\).

## Latent heat and changes of state

During melting, freezing, boiling, or condensing, temperature stays constant while heat is absorbed or released to break or form bonds between particles: \(Q = mL\), where \(L\) is the specific latent heat.

Example 2: Find the heat needed to melt 0.5 kg of ice at 0°C (specific latent heat of fusion of ice = 334,000 J/kg).
\(Q = mL = 0.5 \times 334{,}000 = 167{,}000\,J = 167\,kJ\).

## The gas laws

Boyle's law (constant temperature): \(P_1V_1 = P_2V_2\). Charles' law (constant pressure): \(\dfrac{V_1}{T_1} = \dfrac{V_2}{T_2}\), with temperature always in kelvin (\(K = °C + 273\)). These combine into \(\dfrac{P_1V_1}{T_1} = \dfrac{P_2V_2}{T_2}\).

Example 3: A gas occupies 2 L at a pressure of 100 kPa. Find its new volume if the pressure increases to 200 kPa at constant temperature.
\(P_1V_1 = P_2V_2\): \(100 \times 2 = 200 \times V_2\), so \(V_2 = 1\,L\).

## Thermal expansion

Most solids, liquids, and gases expand when heated because increased particle vibration pushes neighbouring particles further apart on average. This is why bridges have expansion gaps and why a thermometer's liquid rises as it warms.""",
        "related_topics": ["General Physics and Measurement", "Properties of Matter and Fluids"],
    },
    {
        "subject": "Physics",
        "topic": "Nuclear and Modern Physics",
        "title": "Nuclear and Modern Physics",
        "summary": "Radioactive decay, half-life calculations, and a first look at the photoelectric effect.",
        "glossary": [
            {"term": "Radioactivity", "definition": "the spontaneous emission of particles or energy from an unstable atomic nucleus"},
            {"term": "Half-life", "definition": "the time taken for half of the radioactive nuclei in a sample to decay"},
            {"term": "Alpha particle", "definition": "a helium nucleus (2 protons + 2 neutrons) emitted during alpha decay"},
            {"term": "Beta particle", "definition": "a fast-moving electron emitted when a neutron converts to a proton during beta decay"},
            {"term": "Isotope", "definition": "atoms of the same element with the same number of protons but different numbers of neutrons"},
        ],
        "content_md": r"""## Types of radioactive decay

In alpha decay, a nucleus emits an alpha particle (\(^4_2He\)), so the mass number drops by 4 and the atomic number drops by 2. In beta decay, a neutron converts into a proton and an electron is emitted, so the atomic number increases by 1 while the mass number is unchanged. Gamma decay releases energy as electromagnetic radiation with no change to mass or atomic number.

Example 1: Write the nuclear equation for the alpha decay of Uranium-238 (atomic number 92).
\(^{238}_{92}U \rightarrow \,^{234}_{90}Th + \,^4_2He\) -- the mass number falls by 4 (238 to 234) and the atomic number falls by 2 (92 to 90, which is thorium).

## Half-life

A radioactive sample's remaining amount after time \(t\) is \(N = N_0\left(\dfrac{1}{2}\right)^{t/T}\), where \(T\) is the half-life.

Example 2: A radioactive sample has a half-life of 10 days. If the initial mass is 80 g, find the mass remaining after 30 days.
30 days is 3 half-lives, so \(N = 80 \times \left(\dfrac{1}{2}\right)^3 = \dfrac{80}{8} = 10\,g\).

## The photoelectric effect

Shining light on certain metal surfaces can knock electrons out of the metal, but only if the light's frequency is above a minimum "threshold frequency" for that metal -- increasing the light's brightness without raising its frequency does not help, which was one of the first clues that light behaves as discrete packets of energy (photons) with energy \(E = hf\), rather than a continuous wave.""",
        "related_topics": ["General Physics and Measurement", "Electricity and Magnetism"],
    },
    {
        "subject": "Physics",
        "topic": "General Physics and Measurement",
        "title": "General Physics and Measurement",
        "summary": "Vectors versus scalars, and how to take accurate readings with a vernier caliper and micrometer screw gauge.",
        "glossary": [
            {"term": "Vector", "definition": "a quantity with both magnitude and direction, e.g. force, velocity, displacement"},
            {"term": "Scalar", "definition": "a quantity with magnitude only, e.g. mass, speed, distance, time"},
            {"term": "SI unit", "definition": "the internationally agreed base unit for a physical quantity, e.g. the metre for length"},
            {"term": "Vernier caliper", "definition": "an instrument for measuring length precisely (to about 0.01 cm) using a sliding scale"},
            {"term": "Micrometer screw gauge", "definition": "an instrument for measuring very small lengths precisely (to about 0.01 mm) using a calibrated screw"},
        ],
        "content_md": r"""## Vectors and scalars

A scalar quantity (mass, speed, distance, time, energy) is fully described by a number and a unit. A vector quantity (force, velocity, displacement, acceleration) needs a direction too. Two vectors at right angles combine using Pythagoras' theorem.

Example 1: Two forces, 3 N and 4 N, act perpendicular to each other on an object. Find the resultant force.
\(R = \sqrt{3^2 + 4^2} = \sqrt{25} = 5\,N\).

## Precision instruments

A vernier caliper has a main scale and a sliding vernier scale; the reading is the main scale value at (or just before) the vernier's zero, plus the vernier scale division that lines up exactly with a main scale mark, multiplied by the instrument's precision (commonly 0.01 cm). A micrometer screw gauge works similarly but measures much smaller lengths, reading a main (sleeve) scale plus a rotating thimble scale, with a typical precision of 0.01 mm -- useful for things like wire diameter or sheet thickness that a ruler can't measure accurately.

Example 2: A vernier caliper's main scale reads 2.3 cm just before the vernier's zero, and the 4th vernier division lines up with a main scale mark, with a precision of 0.01 cm. Find the reading.
Reading = main scale + (vernier division \(\times\) precision) = \(2.3 + (4 \times 0.01) = 2.34\,cm\).

## Why measurement precision matters

Every measuring instrument has a limit to how finely it can distinguish two close values -- using a tool with too little precision for the quantity being measured (e.g. an ordinary ruler for a wire's diameter) produces a result that looks confident but hides real uncertainty. JAMB often tests whether you can correctly read an instrument's scale, not just whether you know the formula that uses the reading afterwards.""",
        "related_topics": ["Mechanics, Motion, and Energy", "Properties of Matter and Fluids"],
    },
    {
        "subject": "Physics",
        "topic": "Properties of Matter and Fluids",
        "title": "Properties of Matter and Fluids",
        "summary": "Density, pressure in fluids, Archimedes' principle and floating, and Hooke's law for springs.",
        "glossary": [
            {"term": "Density", "definition": "mass per unit volume of a substance, \\(\\rho = \\dfrac{m}{V}\\)"},
            {"term": "Pressure", "definition": "force acting per unit area"},
            {"term": "Upthrust", "definition": "the upward force a fluid exerts on an object submerged (fully or partly) in it"},
            {"term": "Archimedes' principle", "definition": "the upthrust on a submerged object equals the weight of fluid it displaces"},
            {"term": "Hooke's law", "definition": "within the elastic limit, the extension of a spring is proportional to the force applied, \\(F = ke\\)"},
        ],
        "content_md": r"""## Density

Density is mass divided by volume: \(\rho = \dfrac{m}{V}\).

Example 1: Find the density of an object with a mass of 250 g and a volume of 50 cm³.
\(\rho = \dfrac{250}{50} = 5\,g/cm^3\).

## Pressure in fluids

Pressure at a depth \(h\) in a fluid of density \(\rho\) is \(P = h\rho g\) -- it depends only on depth and density, not on the shape or size of the container.

Example 2: Find the pressure at a depth of 5 m in water (density 1000 kg/m³, \(g = 10\,m/s^2\)).
\(P = h\rho g = 5 \times 1000 \times 10 = 50{,}000\,Pa = 50\,kPa\).

## Archimedes' principle and floating

Any object in a fluid experiences an upward force (upthrust) equal to the weight of fluid it displaces. An object floats when this upthrust equals its own weight; it sinks when its weight exceeds the maximum possible upthrust.

Example 3: A block of wood with a submerged volume of 150 cm³ floats in water (density of water = 1000 kg/m³, \(g = 10\,m/s^2\)). Find the upthrust acting on it.
Upthrust = weight of water displaced = \(V\rho g = (150\times10^{-6}) \times 1000 \times 10 = 1.5\,N\).

## Elasticity and Hooke's law

Within a spring's elastic limit, extension is proportional to the applied force: \(F = ke\), where \(k\) is the spring constant. Beyond the elastic limit, the spring is permanently deformed and no longer returns to its original length.

Example 4: A spring stretches 4 cm under a force of 8 N. Find the spring constant.
\(k = \dfrac{F}{e} = \dfrac{8}{0.04} = 200\,N/m\).""",
        "related_topics": ["Mechanics, Motion, and Energy", "Heat and Thermodynamics"],
    },
    {
        "subject": "Physics",
        "topic": "Electronics and Alternating Current",
        "title": "Electronics and Alternating Current",
        "summary": "The difference between AC and DC, RMS values, transformers, and the basics of diodes and rectification.",
        "glossary": [
            {"term": "Alternating current (AC)", "definition": "current that regularly reverses direction, typically varying sinusoidally with time"},
            {"term": "Direct current (DC)", "definition": "current that flows in one direction only"},
            {"term": "RMS value", "definition": "the steady DC-equivalent value of an AC quantity that would deliver the same average power"},
            {"term": "Transformer", "definition": "a device that changes an AC voltage using two coils linked by a shared magnetic field"},
            {"term": "Diode", "definition": "a component that allows current to flow through it in one direction only"},
            {"term": "Rectification", "definition": "the process of converting alternating current into direct current"},
        ],
        "content_md": r"""## AC vs DC and RMS values

Mains electricity is AC: it reverses direction many times per second (50 Hz in Nigeria), unlike the steady DC from a battery. Because AC constantly changes, its effective value for delivering power is quoted as an RMS (root-mean-square) value: \(V_{rms} = \dfrac{V_{peak}}{\sqrt{2}}\).

Example 1: An AC supply has a peak voltage of 340 V. Find its RMS voltage.
\(V_{rms} = \dfrac{340}{\sqrt{2}} = \dfrac{340}{1.414} \approx 240\,V\) -- close to Nigeria's standard 230 V mains supply.

## Transformers

A transformer changes AC voltage using two coils wound on a shared iron core: \(\dfrac{V_p}{V_s} = \dfrac{N_p}{N_s}\), where \(N\) is the number of turns on each coil. A step-up transformer has more turns on the secondary; a step-down transformer has fewer.

Example 2: A transformer has 100 turns on its primary coil and 500 turns on its secondary. If the primary voltage is 12 V, find the secondary voltage.
\(V_s = V_p \times \dfrac{N_s}{N_p} = 12 \times \dfrac{500}{100} = 60\,V\) -- this is a step-up transformer.

## Diodes and rectification

A diode conducts current in only one direction, blocking it in the other. This makes diodes useful for rectification -- converting the back-and-forth current of AC into the one-directional current (DC) that most electronic devices need. A single diode gives half-wave rectification (only one half of each AC cycle passes through); four diodes arranged in a bridge give full-wave rectification, using both halves of the cycle.

## Transistors

A transistor is a semiconductor device that can act as an electronic switch or amplifier -- a small current or voltage at one terminal controls a much larger current flowing between the other two. This switching ability is the basis of all modern digital electronics.""",
        "related_topics": ["Electricity and Magnetism", "General Physics and Measurement"],
    },
    {
        "subject": "Chemistry",
        "topic": "Atomic Structure and Chemical Bonding",
        "title": "Atomic Structure and Chemical Bonding",
        "summary": "How atoms are built, how electrons arrange themselves in shells, and how ionic and covalent bonds form.",
        "glossary": [
            {"term": "Atomic number", "definition": "the number of protons in an atom's nucleus, symbol Z -- it defines the element"},
            {"term": "Mass number", "definition": "the total number of protons and neutrons in an atom's nucleus, symbol A"},
            {"term": "Isotope", "definition": "atoms of the same element with the same atomic number but different mass numbers"},
            {"term": "Ionic bond", "definition": "a bond formed by the electrostatic attraction between oppositely charged ions, usually metal + non-metal"},
            {"term": "Covalent bond", "definition": "a bond formed by two atoms (usually non-metals) sharing a pair of electrons"},
            {"term": "Electron configuration", "definition": "how an atom's electrons are arranged into shells around the nucleus"},
        ],
        "content_md": r"""## Atomic structure

An atom has a nucleus (protons and neutrons) surrounded by electrons. The atomic number \(Z\) equals the number of protons (and, in a neutral atom, the number of electrons too); the mass number \(A\) equals protons plus neutrons.

Example 1: An atom has atomic number 17 and mass number 35. Find its number of protons, electrons, and neutrons.
Protons = electrons = atomic number = 17. Neutrons = mass number - atomic number = 35 - 17 = 18.

## Electron configuration

Electrons fill shells around the nucleus in order, with each shell holding a maximum number of electrons (2, 8, 8 for the first three shells in simple cases). Writing an atom's electron configuration means listing how many electrons sit in each shell, starting from the one closest to the nucleus.

Example 2: Write the electron configuration of sodium (atomic number 11).
11 electrons fill as 2, 8, 1 -- the first shell takes 2, the second takes 8, and the single electron left goes into the third shell. This lone outer electron is why sodium is so reactive.

## Ionic bonding

Ionic bonds form when a metal atom transfers one or more electrons to a non-metal atom, producing a positive ion (cation) and a negative ion (anion) that are held together by electrostatic attraction.

Example 3: Explain how sodium chloride (NaCl) forms.
Sodium (2,8,1) loses its single outer electron to become \(Na^+\) (2,8), and chlorine (2,8,7) gains that electron to become \(Cl^-\) (2,8,8). Both ions now have full outer shells, and the oppositely charged ions attract to form the ionic compound NaCl.

## Covalent bonding

Covalent bonds form when two non-metal atoms each contribute an electron to a shared pair, letting both atoms count that pair towards a full outer shell.

Example 4: Explain the bonding in a water molecule, \(H_2O\).
Oxygen needs 2 more electrons for a full outer shell; each hydrogen atom needs 1 more. Oxygen shares one electron pair with each of the two hydrogen atoms, giving two covalent O-H bonds and completing all three atoms' outer shells.""",
        "related_topics": ["Periodicity and Inorganic Chemistry", "Electrochemistry and Redox Reactions"],
    },
    {
        "subject": "Chemistry",
        "topic": "Acids, Bases, and Salts",
        "title": "Acids, Bases, and Salts",
        "summary": "The pH scale, neutralization reactions, how salts are prepared, and how indicators show whether a substance is acidic or basic.",
        "glossary": [
            {"term": "Acid", "definition": "a substance that produces hydrogen ions (\\(H^+\\)) when dissolved in water"},
            {"term": "Base", "definition": "a substance that produces hydroxide ions (\\(OH^-\\)) when dissolved in water, or that reacts with an acid to form a salt"},
            {"term": "Salt", "definition": "an ionic compound formed when the hydrogen ion of an acid is replaced by a metal or ammonium ion"},
            {"term": "pH", "definition": "a scale from 0 to 14 measuring acidity/alkalinity -- below 7 is acidic, 7 is neutral, above 7 is alkaline"},
            {"term": "Neutralization", "definition": "the reaction between an acid and a base to form a salt and water"},
            {"term": "Indicator", "definition": "a substance that changes colour depending on whether a solution is acidic, neutral, or basic"},
        ],
        "content_md": r"""## Acids and bases

An acid releases \(H^+\) ions in water; a base releases \(OH^-\) ions (or accepts \(H^+\) ions, in the broader definition). The pH scale runs from 0 (strongly acidic) through 7 (neutral) to 14 (strongly alkaline).

## Neutralization

When an acid reacts with a base, the \(H^+\) and \(OH^-\) ions combine to form water, and the remaining ions form a salt: acid + base \(\rightarrow\) salt + water.

Example 1: Write the equation for the neutralization of hydrochloric acid with sodium hydroxide.
\(HCl + NaOH \rightarrow NaCl + H_2O\) -- the salt formed is sodium chloride.

## Preparing salts

Soluble salts are commonly prepared by titration (reacting a measured acid with a base using an indicator to find the exact neutralization point) or by reacting an acid with an excess of a metal, insoluble base, or carbonate and then filtering off the unreacted excess. Insoluble salts are prepared by precipitation -- mixing two soluble solutions so their ions combine to form an insoluble solid that can be filtered out.

Example 2: Describe how to prepare solid copper(II) sulfate crystals from copper(II) oxide and dilute sulfuric acid.
Add excess copper(II) oxide to warm dilute sulfuric acid until no more dissolves (this ensures all the acid has reacted). Filter off the unreacted excess oxide, then heat the blue filtrate gently to evaporate some water and leave it to cool -- copper(II) sulfate crystals form as the solution cools.

## Indicators

Litmus turns red in acid and blue in alkali. Phenolphthalein is colourless in acid and pink in alkali. Universal indicator gives a range of colours corresponding to the approximate pH value, making it useful for estimating strength as well as identifying acid or base.""",
        "related_topics": ["Quantitative Chemistry", "Chemistry of Metals"],
    },
    {
        "subject": "Chemistry",
        "topic": "Organic Chemistry",
        "title": "Organic Chemistry",
        "summary": "Hydrocarbons, homologous series, functional groups, and the naming rules behind alkanes and alkenes.",
        "glossary": [
            {"term": "Hydrocarbon", "definition": "a compound containing only carbon and hydrogen atoms"},
            {"term": "Homologous series", "definition": "a family of compounds with the same general formula and similar chemical properties, differing by a \\(CH_2\\) unit each step"},
            {"term": "Functional group", "definition": "a specific group of atoms within a molecule responsible for its characteristic chemical reactions"},
            {"term": "Saturated", "definition": "containing only single bonds between carbon atoms (as in alkanes)"},
            {"term": "Unsaturated", "definition": "containing at least one double or triple bond between carbon atoms (as in alkenes and alkynes)"},
        ],
        "content_md": r"""## Alkanes

Alkanes are saturated hydrocarbons (only single C-C bonds) with the general formula \(C_nH_{2n+2}\). They're named with a prefix showing the number of carbons (meth-, eth-, prop-, but-...) plus the ending "-ane".

Example 1: Give the molecular formula of propane, and state how many hydrogen atoms it has.
Propane has 3 carbons, so using \(C_nH_{2n+2}\): \(C_3H_{2(3)+2} = C_3H_8\), meaning 8 hydrogen atoms.

## Alkenes

Alkenes are unsaturated hydrocarbons containing at least one C=C double bond, with the general formula \(C_nH_{2n}\), named with the ending "-ene". Because of the double bond, alkenes are more reactive than alkanes and decolourise bromine water, while alkanes do not -- this is the standard chemical test used to tell them apart.

Example 2: A hydrocarbon decolourises bromine water. What does this tell you about the compound, and give its likely general formula?
Decolourising bromine water indicates the presence of a C=C double bond, so the compound is unsaturated -- an alkene, with general formula \(C_nH_{2n}\).

## Functional groups

A functional group determines a molecule's typical reactions regardless of how long its carbon chain is. Alcohols contain the \(-OH\) group and are named with the ending "-ol" (e.g. ethanol, \(C_2H_5OH\)). Carboxylic acids contain the \(-COOH\) group and are named with the ending "-oic acid" (e.g. ethanoic acid, \(CH_3COOH\), the acid in vinegar).

## Isomerism

Structural isomers are compounds with the same molecular formula but different arrangements of atoms, giving them different properties. For example, both butane and methylpropane share the formula \(C_4H_{10}\), but butane has a straight chain of 4 carbons while methylpropane has a branched chain -- different structures, same formula.""",
        "related_topics": ["Quantitative Chemistry", "Physical Chemistry"],
    },
    {
        "subject": "Chemistry",
        "topic": "Chemistry of Non-metals and Gases",
        "title": "Chemistry of Non-metals and Gases",
        "summary": "How common laboratory gases are prepared and identified, and general trends in non-metal chemistry.",
        "glossary": [
            {"term": "Non-metal", "definition": "an element that tends to gain or share electrons in reactions, typically forming acidic or neutral oxides"},
            {"term": "Allotrope", "definition": "different structural forms of the same element in the same physical state, e.g. diamond and graphite (both carbon)"},
            {"term": "Test for a gas", "definition": "a simple observation used to identify a gas, e.g. a glowing splint relighting in oxygen"},
        ],
        "content_md": r"""## Preparing common laboratory gases

Oxygen is prepared by decomposing hydrogen peroxide with manganese(IV) oxide as a catalyst. Hydrogen is prepared by reacting a reactive metal (like zinc) with a dilute acid. Carbon dioxide is prepared by reacting a carbonate (like marble chips) with dilute hydrochloric acid. Ammonia is prepared by gently heating an ammonium salt with a base like calcium hydroxide.

Example 1: Write the word equation for preparing carbon dioxide from marble chips and dilute hydrochloric acid.
Calcium carbonate + hydrochloric acid \(\rightarrow\) calcium chloride + water + carbon dioxide.

## Testing for gases

Each common gas has a simple, reliable test: a glowing splint relights in oxygen; a lit splint produces a "pop" sound in hydrogen; limewater turns milky (cloudy) when carbon dioxide is bubbled through it; damp red litmus paper turns blue in ammonia (confirming an alkaline gas); and damp blue litmus paper turns red then bleaches white in chlorine.

Example 2: A gas turns limewater milky. Identify the gas and explain the chemistry behind the test.
The gas is carbon dioxide. It reacts with the calcium hydroxide dissolved in limewater to form insoluble calcium carbonate, which is the fine white solid that makes the limewater look milky/cloudy.

## General trends among non-metals

Non-metals typically have low melting and boiling points (compared to metals), are poor conductors of heat and electricity (except graphite), and form acidic or neutral oxides when burned in oxygen -- in contrast to metals, whose oxides are typically basic.""",
        "related_topics": ["Atomic Structure and Chemical Bonding", "Environmental and Industrial Chemistry"],
    },
    {
        "subject": "Chemistry",
        "topic": "Physical Chemistry",
        "title": "Physical Chemistry",
        "summary": "What speeds up or slows down a reaction, how equilibrium responds to change, and the difference between exothermic and endothermic reactions.",
        "glossary": [
            {"term": "Rate of reaction", "definition": "how quickly reactants are converted to products, often measured as change in concentration over time"},
            {"term": "Catalyst", "definition": "a substance that speeds up a reaction without being used up itself"},
            {"term": "Chemical equilibrium", "definition": "a state in a reversible reaction where the forward and reverse reaction rates are equal, so concentrations stay constant"},
            {"term": "Le Chatelier's principle", "definition": "if a system at equilibrium is disturbed, it shifts to partially counteract the disturbance"},
            {"term": "Exothermic reaction", "definition": "a reaction that releases heat energy to the surroundings"},
            {"term": "Endothermic reaction", "definition": "a reaction that absorbs heat energy from the surroundings"},
        ],
        "content_md": r"""## What affects reaction rate

Four factors speed up most reactions: higher temperature (particles move faster and collide harder/more often), higher concentration (more particles in a given volume means more frequent collisions), greater surface area of a solid reactant (more particles exposed for collision), and a catalyst (provides an alternative reaction pathway with lower activation energy).

Example 1: Powdered calcium carbonate reacts faster with hydrochloric acid than an equal mass of marble chips. Explain why.
Powdered calcium carbonate has a much greater surface area than the same mass in chip form, exposing more particles to collide with acid particles at any moment, so the reaction proceeds faster.

## Chemical equilibrium and Le Chatelier's principle

In a reversible reaction at equilibrium, both the forward and reverse reactions are still happening, just at equal rates, so overall concentrations appear constant. Le Chatelier's principle predicts that increasing a reactant's concentration, increasing pressure (for gas reactions with fewer moles on one side), or changing temperature will shift the equilibrium position to partially oppose that change.

## Exothermic and endothermic reactions

Exothermic reactions release heat, so the surroundings get warmer (e.g. combustion, neutralization). Endothermic reactions absorb heat, so the surroundings get colder (e.g. dissolving ammonium nitrate in water, thermal decomposition).

Example 2: When solid ammonium nitrate is dissolved in water, the temperature of the solution drops. Classify this process and explain what "drops" tells you.
This is endothermic -- the process absorbs heat energy from its surroundings (the water and solution) to break apart the solid's structure, which is why the temperature you measure decreases.""",
        "related_topics": ["Electrochemistry and Redox Reactions", "Organic Chemistry"],
    },
    {
        "subject": "Chemistry",
        "topic": "Periodicity and Inorganic Chemistry",
        "title": "Periodicity and Inorganic Chemistry",
        "summary": "How the periodic table is organized, and the trends in atomic size, ionization energy, and reactivity across periods and down groups.",
        "glossary": [
            {"term": "Group", "definition": "a vertical column in the periodic table -- elements in the same group have the same number of outer-shell electrons"},
            {"term": "Period", "definition": "a horizontal row in the periodic table -- elements in the same period have the same number of electron shells"},
            {"term": "Atomic radius", "definition": "a measure of the size of an atom, from the nucleus to the outer edge of its electron cloud"},
            {"term": "Ionization energy", "definition": "the energy needed to remove one electron from an atom in its gaseous state"},
            {"term": "Electronegativity", "definition": "a measure of how strongly an atom attracts a shared pair of electrons in a covalent bond"},
        ],
        "content_md": r"""## How the periodic table is organized

Elements are arranged in order of increasing atomic number. Elements in the same group (column) have the same number of electrons in their outer shell, giving them similar chemical properties. Elements in the same period (row) have the same number of electron shells, but the number of outer electrons increases across the period.

## Trends across a period

Moving left to right across a period, atomic radius decreases (more protons pull the same number of shells in tighter), ionization energy increases (electrons are held more tightly), and electronegativity increases (atoms attract bonding electrons more strongly).

## Trends down a group

Moving down a group, atomic radius increases (an extra electron shell is added each time), and ionization energy decreases (outer electrons are further from the nucleus and more shielded, so easier to remove). This is why reactivity of Group 1 metals (like sodium and potassium) increases going down the group, while reactivity of Group 7 non-metals (like fluorine and chlorine) decreases going down the group.

Example 1: Explain why potassium is more reactive than sodium, even though both are Group 1 metals.
Potassium's outer electron is in a shell further from the nucleus than sodium's, and is shielded by more inner electron shells. This makes potassium's outer electron easier to lose, so potassium reacts more vigorously (e.g. with water) than sodium.""",
        "related_topics": ["Atomic Structure and Chemical Bonding", "Chemistry of Metals"],
    },
    {
        "subject": "Chemistry",
        "topic": "Electrochemistry and Redox Reactions",
        "title": "Electrochemistry and Redox Reactions",
        "summary": "Oxidation and reduction, assigning oxidation numbers, and how electrolysis uses electricity to drive a chemical reaction.",
        "glossary": [
            {"term": "Oxidation", "definition": "the loss of electrons (or gain of oxygen, or increase in oxidation number)"},
            {"term": "Reduction", "definition": "the gain of electrons (or loss of oxygen, or decrease in oxidation number)"},
            {"term": "Redox reaction", "definition": "a reaction in which oxidation and reduction happen simultaneously"},
            {"term": "Oxidation number", "definition": "a number assigned to an atom showing its degree of oxidation, used to track electron transfer"},
            {"term": "Electrolysis", "definition": "using electrical energy to drive a non-spontaneous chemical reaction, splitting a compound into its elements"},
        ],
        "content_md": r"""## Oxidation and reduction

Oxidation is loss of electrons; reduction is gain of electrons -- remembered by the mnemonic OIL RIG (Oxidation Is Loss, Reduction Is Gain). Every redox reaction involves both happening together: one species is oxidized while another is reduced.

Example 1: In the reaction \(Zn + Cu^{2+} \rightarrow Zn^{2+} + Cu\), identify what is oxidized and what is reduced.
Zinc goes from 0 to +2, losing 2 electrons -- it is oxidized. Copper goes from +2 to 0, gaining 2 electrons -- it is reduced.

## Oxidation numbers

Oxidation numbers track how "oxidized" an atom is in a compound. Free elements have an oxidation number of 0. Simple ions have an oxidation number equal to their charge. In compounds, oxygen is usually -2 and hydrogen is usually +1; the oxidation numbers in a neutral compound must add up to 0 (or to the ion's overall charge).

Example 2: Find the oxidation number of sulfur in sulfuric acid, \(H_2SO_4\).
Hydrogen contributes \(2 \times (+1) = +2\); oxygen contributes \(4 \times (-2) = -8\). The compound is neutral, so sulfur's oxidation number \(x\) satisfies \(+2 + x - 8 = 0\), giving \(x = +6\).

## Electrolysis

Electrolysis passes an electric current through a molten ionic compound or a solution containing ions, splitting it apart. Positive ions (cations) move to the negative electrode (cathode) and gain electrons (reduction); negative ions (anions) move to the positive electrode (anode) and lose electrons (oxidation). This is how reactive metals like aluminium are extracted from their molten ores, and how compounds like water can be split into hydrogen and oxygen.""",
        "related_topics": ["Chemistry of Metals", "Atomic Structure and Chemical Bonding"],
    },
    {
        "subject": "Chemistry",
        "topic": "Environmental and Industrial Chemistry",
        "title": "Environmental and Industrial Chemistry",
        "summary": "Air and water pollution, the greenhouse effect, and two major industrial processes: the Haber process and the Contact process.",
        "glossary": [
            {"term": "Pollution", "definition": "the introduction of harmful substances into the environment"},
            {"term": "Greenhouse effect", "definition": "the trapping of heat in the atmosphere by gases like carbon dioxide and methane"},
            {"term": "Haber process", "definition": "the industrial method for manufacturing ammonia from nitrogen and hydrogen"},
            {"term": "Contact process", "definition": "the industrial method for manufacturing sulfuric acid, via sulfur trioxide"},
            {"term": "Acid rain", "definition": "rain made abnormally acidic by dissolved pollutant gases like sulfur dioxide and nitrogen oxides"},
        ],
        "content_md": r"""## Air and water pollution

Common air pollutants include carbon monoxide (from incomplete combustion), sulfur dioxide (from burning fuels containing sulfur impurities), and oxides of nitrogen (from vehicle engines at high temperature). Water pollution comes from sources like industrial waste, sewage, and agricultural runoff (fertilizers and pesticides), which can cause excessive algae growth (eutrophication) that starves water of oxygen.

## The greenhouse effect and acid rain

Carbon dioxide and methane trap heat radiating from the Earth's surface, warming the atmosphere -- a natural process made stronger by human activity like burning fossil fuels. Separately, sulfur dioxide and nitrogen oxides dissolve in atmospheric moisture to form dilute sulfuric and nitric acids, falling as acid rain that damages plants, buildings, and aquatic ecosystems.

## The Haber process

The Haber process manufactures ammonia from its elements: \(N_2 + 3H_2 \rightleftharpoons 2NH_3\). It uses a moderately high temperature and high pressure, with an iron catalyst to speed up reaching equilibrium -- ammonia is a key raw material for nitrogen-based fertilizers.

Example 1: Why is the Haber process reaction written with a reversible arrow, \(\rightleftharpoons\)?
Because the reaction doesn't go to completion -- under the reaction conditions, ammonia can also decompose back into nitrogen and hydrogen, so the system reaches a dynamic equilibrium rather than fully converting all reactants to product.

## The Contact process

The Contact process manufactures sulfuric acid. Sulfur is burned to form sulfur dioxide, which is then oxidized (using a vanadium(V) oxide catalyst) to sulfur trioxide, which is finally reacted with water (via an intermediate step) to form concentrated sulfuric acid -- one of the most widely used industrial chemicals, for fertilizers, detergents, and more.""",
        "related_topics": ["Chemistry of Non-metals and Gases", "Physical Chemistry"],
    },
    {
        "subject": "Chemistry",
        "topic": "Chemistry of Metals",
        "title": "Chemistry of Metals",
        "summary": "The reactivity series, how metals are extracted based on their reactivity, and why metals corrode.",
        "glossary": [
            {"term": "Reactivity series", "definition": "a list of metals ordered from most to least reactive, based on how readily they lose electrons"},
            {"term": "Ore", "definition": "a naturally occurring rock or mineral from which a metal can be economically extracted"},
            {"term": "Displacement reaction", "definition": "a reaction where a more reactive metal takes the place of a less reactive metal in a compound"},
            {"term": "Corrosion", "definition": "the gradual destruction of a metal by chemical reaction with its environment, e.g. rusting of iron"},
            {"term": "Alloy", "definition": "a mixture of a metal with one or more other elements, usually another metal, to improve its properties"},
        ],
        "content_md": r"""## The reactivity series

Metals can be ranked by how readily they react (lose electrons to form positive ions), from most reactive (potassium, sodium, calcium) down to least reactive (gold, unreactive metals near the bottom). A more reactive metal will displace a less reactive one from its compound in solution.

Example 1: Predict whether a reaction occurs when zinc metal is placed in copper(II) sulfate solution, and write the equation if so.
Zinc is more reactive than copper, so it displaces copper from solution: \(Zn + CuSO_4 \rightarrow ZnSO_4 + Cu\). A layer of copper forms on the zinc, and the blue colour of the solution fades as copper ions are used up.

## Extraction of metals

A metal's extraction method depends on its position in the reactivity series. Very reactive metals (like aluminium) are extracted by electrolysis of their molten ore, since chemical reduction isn't powerful enough to free them. Moderately reactive metals (like iron) are extracted by reduction with carbon (in a blast furnace) or carbon monoxide, which is cheaper than electrolysis. Unreactive metals (like gold) can occur naturally as the free element and need no chemical extraction at all.

## Corrosion and its prevention

Iron rusts when it reacts with both oxygen and water together, forming hydrated iron(III) oxide. Rusting is prevented by excluding oxygen and/or water from the metal's surface -- painting, oiling, galvanizing (coating with a layer of zinc, which also protects sacrificially even if scratched), or alloying with other metals (like chromium, to make stainless steel).""",
        "related_topics": ["Periodicity and Inorganic Chemistry", "Electrochemistry and Redox Reactions"],
    },
    {
        "subject": "Chemistry",
        "topic": "Quantitative Chemistry",
        "title": "Quantitative Chemistry",
        "summary": "The mole concept, empirical and molecular formulas, and calculations from balanced chemical equations.",
        "glossary": [
            {"term": "Mole", "definition": "the SI unit for amount of substance -- one mole contains \\(6.02 \\times 10^{23}\\) particles (Avogadro's number)"},
            {"term": "Molar mass", "definition": "the mass of one mole of a substance, in grams per mole, numerically equal to its relative formula mass"},
            {"term": "Empirical formula", "definition": "the simplest whole-number ratio of atoms of each element in a compound"},
            {"term": "Molarity", "definition": "the concentration of a solution, measured in moles of solute per litre of solution"},
        ],
        "content_md": r"""## The mole concept

The number of moles of a substance is its mass divided by its molar mass: \(n = \dfrac{mass}{M}\).

Example 1: Find the number of moles in 20 g of calcium carbonate, \(CaCO_3\) (molar mass = 100 g/mol).
\(n = \dfrac{20}{100} = 0.2\,mol\).

## Empirical and molecular formulas

The empirical formula is found from the ratio of moles of each element in a compound; the molecular formula is a whole-number multiple of the empirical formula, found by comparing the empirical formula's mass to the compound's actual molar mass.

Example 2: A compound contains 40% carbon, 6.7% hydrogen, and 53.3% oxygen by mass. Find its empirical formula (relative atomic masses: C = 12, H = 1, O = 16).
Moles: C = \(\dfrac{40}{12} = 3.33\), H = \(\dfrac{6.7}{1} = 6.7\), O = \(\dfrac{53.3}{16} = 3.33\). Dividing by the smallest (3.33): C : H : O = 1 : 2 : 1, giving the empirical formula \(CH_2O\).

## Calculations from equations

A balanced equation's coefficients give the mole ratio between reactants and products, which lets you calculate one substance's mass or volume from another's.

Example 3: Find the mass of carbon dioxide produced when 10 g of calcium carbonate is fully decomposed: \(CaCO_3 \rightarrow CaO + CO_2\) (molar mass \(CaCO_3\) = 100 g/mol, \(CO_2\) = 44 g/mol).
Moles of \(CaCO_3\) = \(\dfrac{10}{100} = 0.1\,mol\). The equation shows a 1:1 ratio, so moles of \(CO_2\) = 0.1 mol, giving a mass of \(0.1 \times 44 = 4.4\,g\).

## Concentration (molarity)

Molarity is moles of solute per litre of solution: \(c = \dfrac{n}{V}\), where \(V\) is in litres.

Example 4: Find the concentration of a solution made by dissolving 0.5 mol of a solute in 250 cm³ of water.
\(250\,cm^3 = 0.25\,L\). \(c = \dfrac{n}{V} = \dfrac{0.5}{0.25} = 2\,mol/L\).""",
        "related_topics": ["Organic Chemistry", "Acids, Bases, and Salts"],
    },
    {
        "subject": "Biology",
        "topic": "Cell Biology and Biochemistry",
        "title": "Cell Biology and Biochemistry",
        "summary": "Plant vs animal cell structure, how substances move across membranes, and the basics of enzymes and biomolecules.",
        "glossary": [
            {"term": "Organelle", "definition": "a specialized structure inside a cell that performs a specific function, e.g. the nucleus or mitochondrion"},
            {"term": "Diffusion", "definition": "the net movement of particles from a region of high concentration to low concentration, needing no energy"},
            {"term": "Osmosis", "definition": "the diffusion of water molecules through a selectively permeable membrane, from high to low water concentration"},
            {"term": "Active transport", "definition": "the movement of particles against a concentration gradient (low to high), which requires energy"},
            {"term": "Enzyme", "definition": "a biological catalyst -- a protein that speeds up a specific reaction without being used up"},
        ],
        "content_md": r"""## Plant vs animal cell structure

Both plant and animal cells share a nucleus (controls the cell and holds genetic material), cytoplasm (where many reactions happen), cell membrane (controls what enters/leaves), and mitochondria (release energy via respiration). Plant cells additionally have a rigid cell wall (support), chloroplasts (photosynthesis), and a large permanent vacuole (storage and support) -- structures animal cells lack.

## Movement across membranes

Diffusion moves particles from high to low concentration and needs no energy -- like a gas spreading through a room. Osmosis is the same idea applied specifically to water crossing a selectively permeable membrane. Active transport moves particles the "wrong way," from low to high concentration, which is why it needs energy (usually from respiration).

Example 1: Root hair cells absorb mineral ions from soil even when the ions are more concentrated inside the cell than in the soil. Which transport process is this, and why?
This is active transport -- moving ions against their concentration gradient (low outside, high inside) requires the cell to spend energy, unlike diffusion or osmosis which happen passively down a gradient.

## Enzymes

Enzymes are biological catalysts that speed up specific reactions by lowering the energy needed to start them, without being used up themselves. Each enzyme has a specific shape that fits its substrate (the "lock and key" model). Enzymes work best within a narrow temperature and pH range; too much heat permanently changes (denatures) their shape, destroying their activity.

Example 2: An enzyme's activity drops sharply above 45°C and does not recover even after cooling back down. Explain why.
High temperature disrupts the enzyme's precise 3D shape (denaturation), including its active site. Since the enzyme's action depends entirely on that shape fitting its substrate, once the shape is permanently destroyed the enzyme can no longer function, even after cooling.

## Biomolecules

Carbohydrates are the body's main energy source. Proteins are needed for growth, repair, and making enzymes/hormones. Lipids (fats and oils) store energy long-term and provide insulation. A balanced diet needs all three in the right proportions, alongside vitamins, minerals, fibre, and water.""",
        "related_topics": ["Genetics and Evolution", "Mammalian Physiology and Anatomy"],
    },
    {
        "subject": "Biology",
        "topic": "Ecology and Environment",
        "title": "Ecology and Environment",
        "summary": "How energy and nutrients flow through ecosystems via food chains, food webs, and cycles like the carbon and nitrogen cycles.",
        "glossary": [
            {"term": "Ecosystem", "definition": "a community of living organisms interacting with each other and their physical environment"},
            {"term": "Producer", "definition": "an organism that makes its own food, usually via photosynthesis, forming the base of a food chain"},
            {"term": "Consumer", "definition": "an organism that gets its energy by eating other organisms"},
            {"term": "Decomposer", "definition": "an organism that breaks down dead organic matter, releasing nutrients back into the ecosystem"},
            {"term": "Food web", "definition": "a network of interconnected food chains showing all the feeding relationships in an ecosystem"},
        ],
        "content_md": r"""## Ecosystem components

An ecosystem includes biotic factors (living things -- plants, animals, microorganisms) and abiotic factors (non-living things -- sunlight, temperature, water, soil). These factors interact constantly: abiotic conditions shape which organisms can survive, and organisms in turn affect their physical environment.

## Food chains and food webs

A food chain shows a single feeding path, always starting with a producer: producer \(\rightarrow\) primary consumer \(\rightarrow\) secondary consumer \(\rightarrow\) tertiary consumer. A food web links many overlapping food chains together, showing that most organisms eat (and are eaten by) more than one other species.

Example 1: In the food chain grass \(\rightarrow\) grasshopper \(\rightarrow\) frog \(\rightarrow\) snake, identify the producer and the secondary consumer.
Grass is the producer (makes its own food via photosynthesis). The grasshopper is the primary consumer (eats the producer), the frog is the secondary consumer (eats the primary consumer), and the snake is the tertiary consumer.

## Energy flow through an ecosystem

Energy enters an ecosystem via producers capturing sunlight, then flows through each feeding level (trophic level) as organisms are eaten. At each transfer, only about 10% of the energy is passed on to the next level -- the rest is lost as heat, used for movement, or lost in waste. This is why food chains rarely have more than 4-5 levels, and why there are always far more producers than top predators.

Example 2: A food chain has 10,000 units of energy available at the producer level. Estimate how much energy reaches the tertiary consumer (three transfers later), using the 10% rule.
Each transfer keeps about 10%: \(10{,}000 \rightarrow 1{,}000 \rightarrow 100 \rightarrow 10\) units -- only about 10 units of the original energy reach the tertiary consumer.

## Nutrient cycles

The carbon cycle moves carbon between the atmosphere (as \(CO_2\)), living organisms (via photosynthesis and respiration), and long-term stores like fossil fuels. The nitrogen cycle moves nitrogen between the atmosphere, soil, and living things via nitrogen fixation (bacteria converting atmospheric nitrogen into usable forms), nitrification, and decomposition -- since plants and animals can't use atmospheric nitrogen gas directly.""",
        "related_topics": ["Agricultural Science and Basic Biology", "Classification"],
    },
    {
        "subject": "Biology",
        "topic": "Animal Biology and Comparative Physiology",
        "title": "Animal Biology and Comparative Physiology",
        "summary": "How the major vertebrate groups differ in their respiration, circulation, and body-temperature control.",
        "glossary": [
            {"term": "Vertebrate", "definition": "an animal with a backbone"},
            {"term": "Ectothermic (cold-blooded)", "definition": "unable to internally regulate body temperature, so it varies with the surroundings"},
            {"term": "Endothermic (warm-blooded)", "definition": "able to internally regulate and maintain a constant body temperature"},
            {"term": "Gill", "definition": "a respiratory organ that extracts dissolved oxygen from water, found in fish"},
        ],
        "content_md": r"""## The five main vertebrate groups

Fish live in water, breathe through gills, and are ectothermic (cold-blooded). Amphibians (like frogs) breathe through both lungs and moist skin, live part of their life in water and part on land, and are also ectothermic. Reptiles have dry scaly skin, breathe with lungs, and are ectothermic. Birds have feathers, breathe with lungs connected to air sacs for highly efficient gas exchange, and are endothermic (warm-blooded). Mammals have hair/fur, breathe with lungs, feed their young with milk from mammary glands, and are endothermic.

Example 1: A student finds an animal with dry scaly skin that lays eggs on land and cannot regulate its own body temperature. Which vertebrate group is this most likely to belong to?
Reptile -- dry scaly skin and an inability to internally regulate body temperature (ectothermic) are both defining reptile features, distinguishing it from the moist skin of amphibians and the fur/feathers of endothermic mammals and birds.

## Respiration adaptations

Fish use gills, which have a large surface area of thin membranes to extract the relatively small amount of oxygen dissolved in water. Amphibians can respire through their moist skin as well as simple lungs. Reptiles, birds, and mammals all use lungs, but bird lungs are uniquely efficient, using connected air sacs to keep air flowing through the lungs in one direction, extracting more oxygen per breath -- useful for the high energy demands of flight.

## Circulatory adaptations

Fish have a two-chambered heart, sending blood through gills for oxygenation, then around the body, before returning -- a single circuit. Amphibians and most reptiles have a three-chambered heart, allowing separate pulmonary (to lungs) and systemic (to body) circuits, though the chambers allow some mixing of oxygenated and deoxygenated blood. Birds and mammals have a four-chambered heart, keeping oxygenated and deoxygenated blood completely separate -- supporting their higher, constant metabolic rate.""",
        "related_topics": ["Mammalian Physiology and Anatomy", "Classification"],
    },
    {
        "subject": "Biology",
        "topic": "Plant Biology",
        "title": "Plant Biology",
        "summary": "Photosynthesis, how plants transport water and food internally, transpiration, and the structure of a flower.",
        "glossary": [
            {"term": "Photosynthesis", "definition": "the process by which plants use light energy to convert carbon dioxide and water into glucose and oxygen"},
            {"term": "Xylem", "definition": "plant tissue that transports water and dissolved minerals upward from the roots"},
            {"term": "Phloem", "definition": "plant tissue that transports dissolved food (mainly sugars) both up and down the plant"},
            {"term": "Transpiration", "definition": "the loss of water vapour from a plant, mainly through pores called stomata on the leaves"},
            {"term": "Stomata", "definition": "tiny pores, mostly on the underside of leaves, that allow gas exchange and water vapour loss"},
        ],
        "content_md": r"""## Photosynthesis

Photosynthesis happens in chloroplasts, using light energy (captured by chlorophyll) to convert carbon dioxide and water into glucose and oxygen: \(6CO_2 + 6H_2O \xrightarrow{light} C_6H_{12}O_6 + 6O_2\).

Example 1: State three factors that can limit the rate of photosynthesis.
Light intensity, carbon dioxide concentration, and temperature can all limit the rate -- whichever of these is in shortest supply relative to the plant's needs becomes the "limiting factor" holding back the overall rate, even if the other two are abundant.

## Plant transport systems

Xylem carries water and dissolved minerals in one direction only: upward from the roots to the leaves. Phloem carries dissolved food (mainly sugar made in photosynthesis) in both directions -- from wherever it's made or stored to wherever it's needed for growth or storage, a process called translocation.

## Transpiration

Transpiration is the loss of water vapour from a plant's surface, mostly through stomata on the leaves. It's a side effect of gas exchange -- stomata must open to let \(CO_2\) in for photosynthesis, and water vapour escapes through the same openings. Transpiration rate increases with higher temperature, lower humidity, more wind, and more light (which opens stomata wider).

Example 2: A plant loses water faster on a hot, windy, sunny day than on a cool, still, cloudy day. Explain why, in terms of transpiration.
Heat and wind both speed up the diffusion and removal of water vapour from the leaf surface, and light causes stomata to open wider for photosynthesis -- all three factors combined increase the transpiration rate, so the plant loses more water in the same amount of time.

## Flower structure and pollination

A typical flower has petals (often colourful, to attract pollinators), sepals (protect the bud), stamens (the male part, producing pollen), and a carpel/pistil (the female part, containing the ovary and ovules). Pollination can be by insects (bright petals, scent, nectar) or by wind (small, dull flowers producing large amounts of light pollen).""",
        "related_topics": ["Cell Biology and Biochemistry", "Agricultural Science and Basic Biology"],
    },
    {
        "subject": "Biology",
        "topic": "Reproduction and Nutrition",
        "title": "Reproduction and Nutrition",
        "summary": "The human reproductive system, the menstrual cycle, and the food classes and deficiency diseases behind a balanced diet.",
        "glossary": [
            {"term": "Fertilization", "definition": "the fusion of a sperm cell and an egg cell to form a zygote"},
            {"term": "Gestation", "definition": "the period of development of a fetus inside the uterus, from fertilization to birth"},
            {"term": "Balanced diet", "definition": "a diet containing the right proportions of carbohydrates, proteins, fats, vitamins, minerals, fibre, and water"},
            {"term": "Deficiency disease", "definition": "an illness caused by a lack of a particular nutrient in the diet"},
        ],
        "content_md": r"""## The human reproductive systems

The male reproductive system produces sperm in the testes, which travel through the sperm duct during ejaculation. The female reproductive system produces eggs in the ovaries; a released egg travels down the oviduct (fallopian tube) towards the uterus, where a fertilized egg can implant and develop.

## The menstrual cycle

The menstrual cycle (roughly 28 days) prepares the female body for a possible pregnancy each month. An egg is released from an ovary around the middle of the cycle (ovulation); the uterus lining thickens to prepare for a fertilized egg. If fertilization doesn't happen, the thickened lining breaks down and is shed as menstruation, and the cycle restarts.

## Fertilization and gestation

Fertilization happens when a sperm cell fuses with an egg cell, usually in the oviduct, forming a zygote that implants in the uterus lining. Gestation (pregnancy) in humans lasts about 9 months, during which the fetus develops and is nourished via the placenta, which lets nutrients and oxygen pass from mother to fetus (and waste pass back) without their blood mixing directly.

## Nutrition and balanced diet

A balanced diet supplies carbohydrates and fats (energy), proteins (growth and repair), vitamins and minerals (specific body functions), fibre (digestion), and water. Lacking a specific nutrient causes a deficiency disease: for example, kwashiorkor results from too little protein (common in children with diets high in starch but low in protein), scurvy results from too little vitamin C, and rickets results from too little vitamin D or calcium (causing weak, poorly formed bones).

Example 1: A child with a swollen belly, thin limbs, and poor growth is diagnosed with kwashiorkor. Which nutrient deficiency causes this, and why does the belly swell?
Kwashiorkor is caused by a severe protein deficiency. The swollen belly happens because low blood protein levels disrupt the normal balance that keeps fluid inside blood vessels, allowing fluid to leak into the abdomen (a symptom called edema).""",
        "related_topics": ["Mammalian Physiology and Anatomy", "Cell Biology and Biochemistry"],
    },
    {
        "subject": "Biology",
        "topic": "Genetics and Evolution",
        "title": "Genetics and Evolution",
        "summary": "How traits are inherited through genes and alleles, working through a monohybrid cross, and the basics of natural selection.",
        "glossary": [
            {"term": "Gene", "definition": "a section of DNA that codes for a particular characteristic"},
            {"term": "Allele", "definition": "one of two or more alternative versions of a gene, e.g. the allele for tall vs short"},
            {"term": "Dominant", "definition": "an allele that is expressed in the phenotype whenever it is present, even with only one copy"},
            {"term": "Recessive", "definition": "an allele that is only expressed in the phenotype when two copies are present (no dominant allele masking it)"},
            {"term": "Genotype", "definition": "the genetic makeup of an organism for a trait, e.g. Tt"},
            {"term": "Phenotype", "definition": "the observable physical characteristic resulting from the genotype, e.g. tall"},
        ],
        "content_md": r"""## Basic genetics terms

Genes come in different versions called alleles. A dominant allele (written with a capital letter, e.g. T) is expressed whenever present; a recessive allele (lowercase, e.g. t) is only expressed when no dominant allele is present -- so an organism needs two recessive alleles (tt) to show the recessive trait, but only one dominant allele (TT or Tt) to show the dominant trait.

## Monohybrid inheritance

Crossing two heterozygous parents (Tt x Tt, each carrying one dominant and one recessive allele) produces offspring in a predictable ratio.

Example 1: Cross two pea plants that are both heterozygous for height (Tt x Tt, where T = tall is dominant, t = short is recessive). Find the expected genotype and phenotype ratios of the offspring.
The possible offspring genotypes are TT, Tt, Tt, and tt (1:2:1). Since both TT and Tt show the tall phenotype (T is dominant), the phenotype ratio is 3 tall : 1 short.

## Natural selection and evolution

Natural selection is the process by which organisms with characteristics better suited to their environment are more likely to survive and reproduce, passing those characteristics to their offspring. Over many generations, this can shift a population's characteristics -- the basis of evolution. Variation within a population (from mutations and sexual reproduction) provides the raw material natural selection acts on.

Example 2: In a population of moths, a dark-coloured variant becomes more common after tree trunks in the area become covered in soot from pollution. Explain this using natural selection.
Against sooty, darkened tree bark, dark moths are better camouflaged from predators than light moths, so more dark moths survive to reproduce. Over generations, the proportion of dark-coloured moths in the population increases -- natural selection favouring the trait best suited to the changed environment.""",
        "related_topics": ["Classification", "Cell Biology and Biochemistry"],
    },
    {
        "subject": "Biology",
        "topic": "Classification",
        "title": "Classification",
        "summary": "The taxonomic hierarchy from kingdom down to species, the five kingdoms of life, and binomial nomenclature.",
        "glossary": [
            {"term": "Taxonomy", "definition": "the science of classifying living organisms into groups based on shared characteristics"},
            {"term": "Species", "definition": "a group of organisms that can interbreed and produce fertile offspring -- the smallest standard taxonomic group"},
            {"term": "Binomial nomenclature", "definition": "the two-part naming system for species, using genus and species names, e.g. Homo sapiens"},
        ],
        "content_md": r"""## The taxonomic hierarchy

Organisms are classified into a nested hierarchy, from broadest to most specific: Kingdom, Phylum, Class, Order, Family, Genus, Species. Each level down contains organisms that are more closely related and share more specific characteristics than the level above.

Example 1: Arrange the following in order from broadest to most specific: Family, Species, Kingdom, Order, Genus, Phylum, Class.
Kingdom, Phylum, Class, Order, Family, Genus, Species -- moving from the largest, most general group down to the smallest, most specific group.

## The five kingdoms

Monera (bacteria -- simple, single-celled organisms with no nucleus), Protista (mostly single-celled organisms with a nucleus, like amoeba), Fungi (organisms that absorb food from their surroundings, like mushrooms and moulds), Plantae (multicellular organisms that photosynthesize), and Animalia (multicellular organisms that consume other organisms for food).

## Binomial nomenclature

Every species has a unique two-part scientific name: the genus name (capitalized) followed by the species name (lowercase), both usually italicized -- for example, Homo sapiens (modern humans) or Oryza sativa (rice). This system gives every organism one standard name recognized worldwide, avoiding the confusion of different common names in different languages or regions.""",
        "related_topics": ["Genetics and Evolution", "Microbiology and Disease"],
    },
    {
        "subject": "Biology",
        "topic": "Mammalian Physiology and Anatomy",
        "title": "Mammalian Physiology and Anatomy",
        "summary": "How the digestive, respiratory, circulatory, and excretory systems work together to keep a mammal alive.",
        "glossary": [
            {"term": "Digestion", "definition": "the breakdown of large food molecules into smaller, absorbable molecules"},
            {"term": "Gas exchange", "definition": "the movement of oxygen and carbon dioxide between the lungs and the blood"},
            {"term": "Circulation", "definition": "the movement of blood around the body, carrying oxygen, nutrients, and waste"},
            {"term": "Excretion", "definition": "the removal of waste products of metabolism from the body, e.g. urea via the kidneys"},
            {"term": "Homeostasis", "definition": "the maintenance of a stable internal environment despite external changes"},
        ],
        "content_md": r"""## The digestive system

Food passes through the mouth (mechanical breakdown, saliva starts starch digestion), esophagus, stomach (acid and enzymes break down proteins), small intestine (most digestion and nutrient absorption happens here, aided by enzymes from the pancreas and bile from the liver), and large intestine (water absorption), before waste leaves via the rectum and anus.

## The respiratory system

Air travels through the trachea into the lungs, branching into bronchi and bronchioles, ending in millions of tiny air sacs called alveoli. Alveoli have thin walls and a large surface area, allowing oxygen to diffuse into the blood and carbon dioxide to diffuse out, into the air to be exhaled.

## The circulatory system

The heart has four chambers: two atria (receive blood) and two ventricles (pump blood out). Blood travels away from the heart in arteries (thick, muscular walls, to withstand high pressure) and back to the heart in veins (thinner walls, with valves to prevent backflow). Capillaries are the tiny vessels where actual exchange of substances with body tissues happens, with walls just one cell thick.

Example 1: Explain why artery walls are much thicker and more muscular than vein walls.
Blood in arteries is under high pressure directly from the heart's pumping, so thick, elastic, muscular walls are needed to withstand that pressure and help push blood along. By the time blood reaches veins, pressure has dropped considerably, so thinner walls (aided by valves and surrounding muscle movement) are sufficient to return blood to the heart.

## The excretory system

The kidneys filter blood, removing waste products (like urea, from protein breakdown) and excess water and salts to form urine, which travels via the ureters to the bladder for storage before being released. This filtering process, carried out by millions of tiny units called nephrons, is essential for maintaining the body's internal water and salt balance (homeostasis).""",
        "related_topics": ["Cell Biology and Biochemistry", "Animal Biology and Comparative Physiology"],
    },
    {
        "subject": "Biology",
        "topic": "Microbiology and Disease",
        "title": "Microbiology and Disease",
        "summary": "The main types of microorganisms, how diseases spread, and how the body defends itself through immunity and vaccination.",
        "glossary": [
            {"term": "Pathogen", "definition": "a microorganism that causes disease"},
            {"term": "Vector", "definition": "an organism that transmits a pathogen from one host to another, e.g. the mosquito for malaria"},
            {"term": "Immunity", "definition": "the body's ability to resist a particular infection, usually by recognizing and destroying the pathogen"},
            {"term": "Vaccine", "definition": "a preparation containing a weakened or inactive pathogen (or part of one), used to trigger immunity without causing disease"},
        ],
        "content_md": r"""## Types of microorganisms

Bacteria are single-celled organisms without a nucleus; some cause disease, but many are harmless or even beneficial. Viruses are much smaller than bacteria and can only reproduce inside a living host cell, hijacking its machinery. Fungi include moulds and yeasts; some cause diseases like athlete's foot or ringworm. Protozoa are single-celled organisms with a nucleus; some, like the Plasmodium parasite, cause serious diseases.

## Disease transmission

Diseases spread through direct contact (touching an infected person or object), airborne droplets (coughing, sneezing), contaminated water or food, or via a vector -- an organism that carries the pathogen from one host to another.

Example 1: Explain how malaria is transmitted, and identify the vector involved.
Malaria is caused by the Plasmodium parasite and transmitted by the bite of an infected female Anopheles mosquito, which acts as the vector -- the mosquito picks up the parasite from one infected person's blood and transmits it to the next person it bites.

## Immunity and vaccination

The body's immune system can develop immunity to a pathogen after exposure, by producing antibodies that recognize and help destroy it, and by "remembering" the pathogen for a faster response if it appears again. A vaccine triggers this same memory response using a weakened, inactive, or partial form of the pathogen that cannot cause the actual disease, giving protection without the risk of getting sick first.""",
        "related_topics": ["Classification", "Ecology and Environment"],
    },
    {
        "subject": "Biology",
        "topic": "Agricultural Science and Basic Biology",
        "title": "Agricultural Science and Basic Biology",
        "summary": "Soil fertility, crop production practices, and the basics of livestock farming.",
        "glossary": [
            {"term": "Soil fertility", "definition": "a soil's ability to supply nutrients needed for healthy plant growth"},
            {"term": "Crop rotation", "definition": "growing different crops in a sequence on the same land, to maintain soil fertility and reduce pests"},
            {"term": "Fertilizer", "definition": "a substance added to soil to supply nutrients and improve plant growth"},
            {"term": "Livestock", "definition": "animals raised for food, labour, or other agricultural products"},
        ],
        "content_md": r"""## Soil and plant growth

Soil fertility depends on its nutrient content (especially nitrogen, phosphorus, and potassium), water-holding capacity, texture (proportion of sand, silt, and clay), and organic matter content. Continuously growing the same crop on the same land depletes specific nutrients that crop needs most, reducing yields over time.

## Crop production practices

Crop rotation -- growing different types of crops in sequence, such as alternating a nitrogen-depleting crop like maize with a nitrogen-fixing legume like beans -- helps restore soil nutrients naturally and breaks the life cycles of pests and diseases that target a specific crop. Fertilizers (organic, like manure and compost, or inorganic, like NPK fertilizer) directly replace nutrients the soil lacks. Pest control methods include chemical pesticides, biological control (introducing natural predators), and good farming practices like weeding and proper spacing.

Example 1: Explain why growing beans after maize on the same plot of land can improve the following season's maize yield.
Maize uses up a lot of soil nitrogen as it grows. Beans (a legume) have root nodules containing bacteria that fix atmospheric nitrogen into the soil, replenishing what the maize depleted -- so the soil has more nitrogen available for the next crop grown there.

## Livestock farming basics

Livestock farming involves raising animals like cattle, goats, poultry, and fish for meat, milk, eggs, or other products. Good livestock management includes providing proper housing, balanced feed and clean water, disease prevention (vaccination, hygiene), and breeding practices suited to the farm's goals (e.g. selecting for higher milk yield or faster growth).""",
        "related_topics": ["Plant Biology", "Ecology and Environment"],
    },
    {
        "subject": "Geography",
        "topic": "Population and Settlement",
        "title": "Population and Settlement",
        "summary": "What controls where people live, how settlements are patterned, and why people move from rural areas to cities.",
        "glossary": [
            {"term": "Population density", "definition": "the number of people living per unit area, e.g. per square kilometre"},
            {"term": "Population distribution", "definition": "the pattern of where people live across an area -- evenly, or clustered in certain places"},
            {"term": "Settlement pattern", "definition": "the arrangement of buildings/homes in a settlement -- nucleated, dispersed, or linear"},
            {"term": "Rural-urban migration", "definition": "the movement of people from the countryside to towns and cities"},
            {"term": "Push factor", "definition": "a negative condition that drives people to leave a place, e.g. lack of jobs"},
            {"term": "Pull factor", "definition": "a positive condition that attracts people to a place, e.g. better healthcare or education"},
        ],
        "content_md": r"""## Population distribution and density

Population density is calculated as \(\text{density} = \dfrac{\text{population}}{\text{land area}}\). Distribution is influenced by climate (people avoid extreme heat, cold, or aridity), relief (flat, low-lying land is easier to settle than steep mountains), soil fertility (good for farming), availability of water, and access to resources or trade routes.

Example 1: A region has a population of 2,400,000 people and covers 8,000 km². Find its population density.
\(\text{density} = \dfrac{2{,}400{,}000}{8{,}000} = 300\) people per km².

## Settlement patterns

A nucleated settlement is tightly clustered around a central point (like a market, water source, or crossroads). A dispersed settlement has scattered, isolated homes, common in farming areas where each family needs land around their house. A linear settlement stretches out along a feature like a road, river, or coastline.

## Urbanization and rural-urban migration

Urbanization is the growing proportion of a population living in towns and cities. Rural-urban migration is driven by push factors in rural areas (limited jobs, poor services, land shortages) and pull factors in urban areas (more job opportunities, better healthcare and education, perceived higher living standards).

Example 2: Explain two consequences of rapid rural-urban migration for a city.
Rapid migration can overwhelm a city's housing supply, leading to slum development and overcrowding, and can strain infrastructure like water supply, sanitation, and transport faster than the city can expand them to cope.""",
        "related_topics": ["Regional Geography of Nigeria/West Africa", "Economic Geography and Trade"],
    },
    {
        "subject": "Geography",
        "topic": "Map Reading and Practical Geography",
        "title": "Map Reading and Practical Geography",
        "summary": "How to use map scale, contour lines, direction/bearing, and grid references to interpret a map.",
        "glossary": [
            {"term": "Scale", "definition": "the ratio between a distance on a map and the actual distance on the ground"},
            {"term": "Contour line", "definition": "a line on a map joining points of equal height above sea level"},
            {"term": "Bearing", "definition": "a direction measured clockwise from north, given as a three-figure angle (000° to 360°)"},
            {"term": "Grid reference", "definition": "a coordinate system used to pinpoint an exact location on a map, using numbered grid lines"},
        ],
        "content_md": r"""## Map scale

A map's scale (e.g. 1:50,000) means 1 unit on the map represents 50,000 of the same unit on the ground. To find the actual distance, measure the map distance and multiply by the scale factor.

Example 1: On a map with a scale of 1:50,000, two towns are 4 cm apart. Find the actual distance between them, in kilometres.
Actual distance = \(4 \times 50{,}000 = 200{,}000\,cm = 2{,}000\,m = 2\,km\).

## Contour lines and relief

Contour lines join points of equal elevation. Widely spaced contours indicate a gentle slope; closely spaced contours indicate a steep slope. Concentric circles of contours (getting smaller as height increases) typically indicate a hill or peak.

## Direction and bearing

Bearings are measured clockwise from north as a three-figure angle, so due north is 000°, due east is 090°, due south is 180°, and due west is 270°.

Example 2: A hiker walks from a point directly towards a landmark that is due south-east of them. State the bearing.
South-east lies exactly between south (180°) and east (090°)... measuring clockwise from north, south-east is 135°.

## Grid references

A grid reference uses two sets of numbered lines on a map (eastings, read left to right, then northings, read bottom to top) to give a precise location, usually as a four or six-figure reference -- the more figures, the more precise the location.""",
        "related_topics": ["Relief, Drainage, and Rocks/Minerals", "Oceanography and Physical Geography"],
    },
    {
        "subject": "Geography",
        "topic": "Oceanography and Physical Geography",
        "title": "Oceanography and Physical Geography",
        "summary": "Ocean currents and their effect on climate, what causes tides, and the major relief features of the ocean floor.",
        "glossary": [
            {"term": "Ocean current", "definition": "a large-scale, continuous movement of ocean water in a set direction"},
            {"term": "Tide", "definition": "the regular rise and fall of sea level, caused mainly by the gravitational pull of the moon (and sun)"},
            {"term": "Continental shelf", "definition": "the shallow, gently sloping seabed surrounding a continent, before it drops steeply into deep ocean"},
        ],
        "content_md": r"""## Ocean currents

Ocean currents are large, persistent movements of water, driven mainly by wind patterns, the Earth's rotation, and differences in water temperature/density. Warm currents (flowing from the tropics towards the poles) raise the temperature of coastal areas they pass; cold currents (flowing from polar regions towards the equator) cool coastal areas and can reduce rainfall by limiting evaporation.

Example 1: Explain why a coastal region next to a warm ocean current tends to have a milder climate than a similar coastal region next to a cold current.
A warm current transfers heat from the ocean water to the air above it, warming the coastal region's climate and often increasing rainfall (more evaporation from the warmer water). A cold current has the opposite effect, cooling the coastal air and often reducing rainfall.

## Tides

Tides are the regular rise and fall of sea level, caused mainly by the gravitational pull of the moon, with a smaller contribution from the sun. Most coastlines experience two high tides and two low tides roughly every 24 hours as the Earth rotates.

## Ocean relief features

The continental shelf is the shallow, gently sloping seabed nearest a continent, where most marine life and fishing activity is concentrated. Beyond it, the continental slope drops more steeply down to the abyssal plain -- the vast, relatively flat deep ocean floor.""",
        "related_topics": ["Relief, Drainage, and Rocks/Minerals", "Weather, Climate, and Ecology"],
    },
    {
        "subject": "Geography",
        "topic": "Economic Geography and Trade",
        "title": "Economic Geography and Trade",
        "summary": "The three sectors of economic activity, and the basics of international trade and balance of trade.",
        "glossary": [
            {"term": "Primary industry", "definition": "economic activity that extracts raw materials directly from nature, e.g. farming, mining, fishing"},
            {"term": "Secondary industry", "definition": "economic activity that processes or manufactures raw materials into finished goods"},
            {"term": "Tertiary industry", "definition": "economic activity that provides services, e.g. banking, transport, education"},
            {"term": "Balance of trade", "definition": "the difference in value between a country's exports and its imports"},
        ],
        "content_md": r"""## The three sectors of economic activity

Primary industries extract raw materials directly from the natural environment -- farming, fishing, forestry, and mining. Secondary industries take those raw materials and process or manufacture them into finished or semi-finished products -- turning cocoa beans into chocolate, or crude oil into refined petroleum products. Tertiary industries provide services rather than physical goods -- banking, healthcare, transport, and education.

Example 1: Classify each of the following as primary, secondary, or tertiary: cocoa farming, a textile factory, a hospital.
Cocoa farming is primary (extracting a raw material directly from the land). A textile factory is secondary (manufacturing raw cotton into finished cloth). A hospital is tertiary (providing a service, not producing a physical good).

## International trade and balance of trade

Countries trade because no country produces everything it needs efficiently -- exporting goods it can produce cheaply or abundantly, and importing goods it lacks or produces less efficiently. The balance of trade is the value of exports minus the value of imports: a positive balance (trade surplus) means a country exports more than it imports; a negative balance (trade deficit) means the opposite.

Example 2: A country exports goods worth $50 billion and imports goods worth $65 billion in a year. Find its balance of trade, and state whether this is a surplus or deficit.
Balance of trade = exports - imports = \(50 - 65 = -15\) billion dollars -- a trade deficit of $15 billion, since imports exceed exports.""",
        "related_topics": ["Industry and Natural Resources", "Population and Settlement"],
    },
    {
        "subject": "Geography",
        "topic": "Regional Geography of Nigeria/West Africa",
        "title": "Regional Geography of Nigeria/West Africa",
        "summary": "Nigeria's major geographic regions, its West African neighbours, and the role of ECOWAS.",
        "glossary": [
            {"term": "Region", "definition": "an area defined by shared physical or human characteristics, e.g. climate, vegetation, or culture"},
            {"term": "ECOWAS", "definition": "the Economic Community of West African States, a regional group promoting economic integration among West African countries"},
        ],
        "content_md": r"""## Nigeria's geographic regions

Nigeria is often divided into broad regions based on relief and vegetation: the coastal/Niger Delta region in the south (mangrove swamps and creeks), the rainforest belt just north of it, the middle belt (guinea savanna, including the Jos Plateau), and the northern region (dominated by Sudan and Sahel savanna, drier and more open). These regional differences shape which crops are farmed, population density, and settlement patterns across the country.

## Nigeria's West African neighbours

Nigeria shares land borders with Benin to the west, Niger to the north, Chad to the north-east, and Cameroon to the east, with the Atlantic Ocean (Gulf of Guinea) to the south.

## ECOWAS

ECOWAS (Economic Community of West African States) is a regional group of West African countries formed to promote economic integration, free movement of people and goods, and cooperation across the region. It allows citizens of member states to travel, trade, and work more freely across borders within West Africa than they could otherwise.""",
        "related_topics": ["Population and Settlement", "Industry and Natural Resources"],
    },
    {
        "subject": "Geography",
        "topic": "Weather, Climate, and Ecology",
        "title": "Weather, Climate, and Ecology",
        "summary": "The elements of weather, the climate types found across Nigeria and West Africa, and the basics of climate change.",
        "glossary": [
            {"term": "Weather", "definition": "the day-to-day state of the atmosphere in a specific place -- temperature, rainfall, wind, etc. at a given time"},
            {"term": "Climate", "definition": "the average weather conditions of a place over a long period, typically 30+ years"},
            {"term": "Humidity", "definition": "the amount of water vapour present in the air"},
        ],
        "content_md": r"""## Elements of weather

Weather is described by several measurable elements: temperature, rainfall, humidity, atmospheric pressure, and wind (speed and direction). Weather changes day to day; climate is the long-term average pattern of these elements for a region.

## Climate types in Nigeria and West Africa

Southern Nigeria has an equatorial/tropical rainforest climate -- high temperatures and heavy rainfall year-round, with two rainy seasons. Moving north, the climate transitions to tropical savanna (wet and dry seasons clearly separated, less total rainfall), and finally to a semi-arid Sahel-type climate in the far north (low, unreliable rainfall and a long dry season).

Example 1: Explain why northern Nigeria receives less rainfall than southern Nigeria.
Southern Nigeria is closer to the coast and the equator, so moisture-laden winds from the Atlantic Ocean bring frequent, heavy rain. Northern Nigeria is further from the ocean's moisture source and more influenced by the dry, dust-laden harmattan winds from the Sahara, resulting in far less and less reliable rainfall.

## Climate change

Climate change refers to long-term shifts in temperature and weather patterns, significantly accelerated by human activities like burning fossil fuels, which increase greenhouse gas concentrations in the atmosphere. Effects relevant to West Africa include shifting rainfall patterns, more frequent extreme weather, and desertification pressure at the Sahel's margins.""",
        "related_topics": ["Oceanography and Physical Geography", "Agriculture and Vegetation"],
    },
    {
        "subject": "Geography",
        "topic": "Relief, Drainage, and Rocks/Minerals",
        "title": "Relief, Drainage, and Rocks/Minerals",
        "summary": "The major landform types, how river drainage systems are organized, and how igneous, sedimentary, and metamorphic rocks form.",
        "glossary": [
            {"term": "Relief", "definition": "the variation in height and shape of the land surface"},
            {"term": "Drainage basin", "definition": "the area of land drained by a river and all its tributaries"},
            {"term": "Igneous rock", "definition": "rock formed from cooled and solidified molten magma or lava"},
            {"term": "Sedimentary rock", "definition": "rock formed from compacted and cemented layers of sediment over time"},
            {"term": "Metamorphic rock", "definition": "rock formed when existing rock is changed by intense heat and/or pressure"},
        ],
        "content_md": r"""## Relief features

Relief describes the shape and elevation of the land: highlands (plateaus, hills, mountains), lowlands (plains, valleys), and everything between. Relief strongly influences drainage, climate, vegetation, and where people settle and farm.

## Drainage patterns

A river's drainage basin is all the land whose water eventually flows into that river system, bounded by a watershed (the high ground separating one drainage basin from a neighbouring one). Common drainage patterns include dendritic (branching like a tree, on uniform rock) and trellis (a rectangular, grid-like pattern, where alternating hard and soft rock bands control tributary direction).

Example 1: A river system's tributaries branch out irregularly in many directions, like the branches of a tree. Identify this drainage pattern and the rock condition that typically produces it.
This is a dendritic drainage pattern, typically found where the underlying rock has uniform resistance to erosion, letting tributaries develop in whatever direction the local slope naturally guides them, rather than being forced into a regular geometric pattern by bands of differing rock hardness.

## Rock types

Igneous rocks form when molten magma or lava cools and solidifies (e.g. granite, forming slowly underground with large crystals; basalt, cooling quickly at the surface with small crystals). Sedimentary rocks form when layers of sediment (sand, mud, shell fragments) are compacted and cemented together over long periods (e.g. sandstone, limestone) -- often containing fossils. Metamorphic rocks form when existing rock is transformed by intense heat and/or pressure, without fully melting (e.g. marble from limestone, slate from mudstone).""",
        "related_topics": ["Weathering, Erosion, and Soils", "Map Reading and Practical Geography"],
    },
    {
        "subject": "Geography",
        "topic": "Weathering, Erosion, and Soils",
        "title": "Weathering, Erosion, and Soils",
        "summary": "The difference between physical and chemical weathering, the main agents of erosion, and how soils form and are structured.",
        "glossary": [
            {"term": "Weathering", "definition": "the breakdown of rock in place, without the fragments being moved away"},
            {"term": "Erosion", "definition": "the wearing away and transport of rock or soil material by agents like water, wind, or ice"},
            {"term": "Soil profile", "definition": "the vertical sequence of distinct layers (horizons) visible in a cross-section of soil"},
            {"term": "Leaching", "definition": "the downward washing of soluble nutrients out of the upper soil layers by percolating water"},
        ],
        "content_md": r"""## Types of weathering

Physical (mechanical) weathering breaks rock apart without changing its chemical composition -- for example, water repeatedly freezing and expanding in cracks, or a rock's outer layers expanding and contracting from daily heating and cooling until they flake off. Chemical weathering changes a rock's chemical composition, weakening it -- for example, rainwater (slightly acidic) dissolving limestone, or oxygen reacting with iron-rich rock to form rust-like compounds.

Example 1: A rock in a hot desert repeatedly heats up strongly during the day and cools sharply at night, eventually cracking and flaking without any change to its mineral composition. Identify the type of weathering.
This is physical (mechanical) weathering -- specifically thermal expansion and contraction -- since the rock breaks apart from repeated stress, with no chemical change to the minerals themselves.

## Agents of erosion

Water erosion (rivers, waves, rainfall runoff) is the most widespread agent, carving valleys and coastlines. Wind erosion is significant in dry, exposed areas with little vegetation to hold soil in place. Ice erosion (glaciers) carves distinctive U-shaped valleys, though this is not significant in most of West Africa's climate.

## Soil formation and the soil profile

Soil forms gradually from weathered rock (the parent material) mixed with organic matter from decomposing plants and animals. A soil profile typically shows distinct horizons: topsoil (dark, nutrient- and organic-matter-rich, where most plant roots and biological activity are), subsoil (lighter, less organic matter, often where leached nutrients accumulate), and weathered parent rock below.""",
        "related_topics": ["Relief, Drainage, and Rocks/Minerals", "Agriculture and Vegetation"],
    },
    {
        "subject": "Geography",
        "topic": "Agriculture and Vegetation",
        "title": "Agriculture and Vegetation",
        "summary": "The natural vegetation belts of Nigeria and the traditional and modern farming systems adapted to them.",
        "glossary": [
            {"term": "Vegetation belt", "definition": "a broad band of characteristic natural plant cover, largely determined by climate"},
            {"term": "Shifting cultivation", "definition": "a farming system where land is cultivated for a few years, then left fallow to recover fertility while a new plot is farmed"},
            {"term": "Savanna", "definition": "vegetation dominated by grassland with scattered trees, typical of areas with a marked wet and dry season"},
        ],
        "content_md": r"""## Vegetation belts of Nigeria

Moving from south to north, Nigeria's natural vegetation shifts with the climate: mangrove swamp forest along the coast, tropical rainforest just inland (dense, evergreen, multiple canopy layers), guinea savanna in the middle belt (mixed grassland and trees), and Sudan/Sahel savanna in the far north (short grass, scattered thorny trees, adapted to low rainfall).

Example 1: Explain why Nigeria's vegetation changes from rainforest in the south to savanna in the north.
Vegetation closely follows rainfall amount and reliability. Southern Nigeria's high, year-round rainfall supports dense rainforest; as rainfall decreases and becomes more seasonal moving north, only more drought-tolerant grassland and scattered trees (savanna) can survive, since full rainforest needs far more consistent moisture than the north receives.

## Farming systems

Shifting cultivation involves farming a plot of land for a few seasons until its fertility drops, then abandoning it to recover naturally (fallow) while a new plot is cleared -- traditional in areas with abundant land and low population density. Mixed farming combines crop growing and livestock rearing on the same farm, letting animal manure fertilize the soil. Modern, more intensive farming methods (irrigation, fertilizers, mechanization) are increasingly used where population pressure makes traditional shifting cultivation impractical.""",
        "related_topics": ["Weathering, Erosion, and Soils", "Weather, Climate, and Ecology"],
    },
    {
        "subject": "Geography",
        "topic": "Industry and Natural Resources",
        "title": "Industry and Natural Resources",
        "summary": "Nigeria's major mineral resources, the factors behind industrial location, and the difference between renewable and non-renewable resources.",
        "glossary": [
            {"term": "Mineral resource", "definition": "a naturally occurring, economically valuable substance extracted from the earth, e.g. petroleum, tin, coal"},
            {"term": "Renewable resource", "definition": "a resource that naturally replenishes over a human timescale, e.g. solar energy, forests (if managed sustainably)"},
            {"term": "Non-renewable resource", "definition": "a resource that exists in a fixed supply and cannot be replaced once used up, e.g. petroleum, coal"},
        ],
        "content_md": r"""## Nigeria's mineral resources

Nigeria's most economically significant mineral resource is petroleum (crude oil), concentrated in the Niger Delta region, alongside natural gas. Other notable resources include coal (historically mined in the Enugu area), tin and columbite (Jos Plateau), and limestone (used for cement, found in various states).

## Factors affecting industrial location

Industries tend to locate where several factors align favourably: availability of raw materials, access to markets for the finished product, transport links, availability of labour, and access to power/energy supply. Heavy, weight-losing industries (where the raw material is bulkier than the finished product) often locate near the raw material source; industries producing bulkier finished goods often locate closer to their markets.

Example 1: Explain why a cement factory is typically built close to a limestone quarry, rather than in a distant city.
Cement production uses large quantities of heavy limestone, and the finished cement is not meaningfully heavier than the limestone used to make it. Building the factory near the quarry avoids the high cost of transporting large volumes of heavy raw material over long distances.

## Renewable vs non-renewable resources

Renewable resources (solar energy, wind, sustainably managed forests, water) can replenish naturally within a human timescale if not overused. Non-renewable resources (petroleum, coal, mineral ores) exist in a fixed quantity and, once extracted and used, cannot be replaced -- making their careful, sustainable management an important economic and environmental concern.""",
        "related_topics": ["Economic Geography and Trade", "Regional Geography of Nigeria/West Africa"],
    },
    {
        "subject": "Economics",
        "topic": "Basic Economic Concepts and Systems",
        "title": "Basic Economic Concepts and Systems",
        "summary": "The fundamental economic problem of scarcity, opportunity cost, and how different economic systems answer the basic economic questions.",
        "glossary": [
            {"term": "Scarcity", "definition": "the basic economic problem that resources are limited while human wants are unlimited"},
            {"term": "Opportunity cost", "definition": "the value of the next best alternative given up when a choice is made"},
            {"term": "Economic system", "definition": "the way a society organizes the production, distribution, and consumption of goods and services"},
            {"term": "Capitalism (market economy)", "definition": "an economic system where resources are privately owned and prices are set by market forces"},
            {"term": "Mixed economy", "definition": "an economic system combining private enterprise with government intervention and ownership"},
        ],
        "content_md": r"""## Scarcity and the economic problem

Every society faces the same basic problem: resources (land, labour, capital) are limited, but human wants are effectively unlimited. This forces every economy to make choices about what to produce, how to produce it, and for whom -- these three questions are the foundation of economics.

## Opportunity cost

Because resources are scarce, choosing to use them one way means giving up the next best alternative use. This forgone alternative is the opportunity cost of the choice made.

Example 1: A farmer has one plot of land and can grow either yam (worth ₦200,000) or cassava (worth ₦150,000) on it, but not both. If she chooses to grow yam, what is her opportunity cost?
Her opportunity cost is the cassava she gave up growing, worth ₦150,000 -- the value of the next best alternative she sacrificed by choosing yam instead.

## Economic systems

A capitalist (market) economy relies on private ownership and market forces (prices, supply and demand) to decide what's produced and how resources are allocated. A socialist (command) economy relies on government/state ownership and central planning to make these decisions. A mixed economy, which most real-world countries (including Nigeria) use, combines private enterprise with government intervention -- the state provides some services and regulates markets, while private businesses handle much of production.""",
        "related_topics": ["Demand, Supply, and Market Structures", "Business Organisation and Government"],
    },
    {
        "subject": "Economics",
        "topic": "Demand, Supply, and Market Structures",
        "title": "Demand, Supply, and Market Structures",
        "summary": "The laws of demand and supply, how market equilibrium price is set, elasticity, and the main types of market structure.",
        "glossary": [
            {"term": "Demand", "definition": "the quantity of a good consumers are willing and able to buy at a given price"},
            {"term": "Supply", "definition": "the quantity of a good producers are willing and able to sell at a given price"},
            {"term": "Equilibrium price", "definition": "the price at which quantity demanded exactly equals quantity supplied"},
            {"term": "Elasticity of demand", "definition": "a measure of how much quantity demanded responds to a change in price"},
            {"term": "Monopoly", "definition": "a market structure with a single seller controlling the entire supply of a good, with no close substitutes"},
        ],
        "content_md": r"""## The laws of demand and supply

The law of demand states that, other things being equal, quantity demanded falls as price rises (and rises as price falls) -- shown as a downward-sloping demand curve. The law of supply states that quantity supplied rises as price rises -- shown as an upward-sloping supply curve, since higher prices make production more profitable.

## Market equilibrium

The equilibrium price is where the demand and supply curves cross -- the price at which quantity demanded exactly equals quantity supplied, with no shortage or surplus.

Example 1: At a price of ₦500, quantity demanded for a good is 200 units and quantity supplied is 350 units. Is the market in equilibrium, and if not, what will likely happen to the price?
The market is not in equilibrium -- supply (350) exceeds demand (200), meaning there's a surplus of 150 units. Sellers will likely lower the price to clear the surplus, moving the market towards equilibrium.

## Elasticity of demand

Elasticity of demand measures how responsive quantity demanded is to a price change. Demand is elastic if a small price change causes a large change in quantity demanded (common for luxuries or goods with many substitutes); demand is inelastic if quantity demanded barely changes with price (common for necessities, like basic food staples or medicine).

Example 2: When the price of a particular brand of soft drink rises by 10%, the quantity demanded falls by 25%. Is demand for this drink elastic or inelastic?
Elastic -- the percentage change in quantity demanded (25%) is larger than the percentage change in price (10%), meaning consumers are quite responsive to the price change, likely because substitute drinks are readily available.

## Market structures

Perfect competition has many small sellers, identical products, and no single seller able to influence price. A monopoly has a single seller with full control over supply and significant power over price. An oligopoly sits between the two -- a few large firms dominate the market, and each firm's pricing decisions noticeably affect its rivals.""",
        "related_topics": ["Theory of Consumer Behaviour", "Basic Economic Concepts and Systems"],
    },
    {
        "subject": "Economics",
        "topic": "Theory of Production and Distribution",
        "title": "Theory of Production and Distribution",
        "summary": "The four factors of production and their rewards, the benefits of division of labour, and the law of diminishing returns.",
        "glossary": [
            {"term": "Factors of production", "definition": "the resources used to produce goods and services: land, labour, capital, and entrepreneurship"},
            {"term": "Division of labour", "definition": "splitting a production process into separate, specialized tasks performed by different workers"},
            {"term": "Law of diminishing returns", "definition": "the principle that adding more of one variable input (while others stay fixed) eventually yields smaller and smaller extra output"},
        ],
        "content_md": r"""## The factors of production and their rewards

Land (all natural resources) earns rent. Labour (human effort, physical and mental) earns wages. Capital (man-made resources used to produce further goods, like machinery and tools) earns interest. Entrepreneurship (organizing the other three factors and bearing business risk) earns profit.

## Division of labour

Dividing a production process into smaller, specialized tasks -- with each worker focusing on one part -- generally increases total output, because workers become faster and more skilled at their specific task, and less time is lost switching between different jobs.

Example 1: Explain one advantage and one disadvantage of division of labour in a factory producing shoes.
Advantage: workers become highly skilled and efficient at their specific narrow task (e.g. only stitching soles), increasing overall output speed. Disadvantage: the repetitive, narrow nature of the work can make jobs monotonous and less satisfying, and workers become dependent on every other stage of the process running smoothly.

## The law of diminishing returns

If more units of one variable factor (say, labour) are added to a fixed amount of another factor (say, land or machinery), output initially rises, but eventually each additional unit of the variable factor adds less extra output than the one before it.

Example 2: A farmer keeps adding more workers to a fixed-size plot of land. Explain why output per additional worker eventually starts to fall.
As more and more workers are added to the same fixed land area, each new worker has less land and fewer tools to work with than the ones before, so their individual contribution to total output shrinks -- this is the law of diminishing returns in action.""",
        "related_topics": ["Basic Economic Concepts and Systems", "Agriculture, Industry, and Petroleum Economics"],
    },
    {
        "subject": "Economics",
        "topic": "Money, Banking, and Public Finance",
        "title": "Money, Banking, and Public Finance",
        "summary": "What money does, how the banking system works, and the basics of taxation and government budgets.",
        "glossary": [
            {"term": "Money", "definition": "anything generally accepted as a medium of exchange for goods and services"},
            {"term": "Central bank", "definition": "the institution responsible for a country's monetary policy and regulating its banking system, e.g. the Central Bank of Nigeria"},
            {"term": "Direct tax", "definition": "a tax paid directly by the person or organization it's levied on, e.g. personal income tax"},
            {"term": "Indirect tax", "definition": "a tax collected by an intermediary (like a retailer) and passed on to the government, e.g. VAT"},
            {"term": "Budget deficit", "definition": "when government spending exceeds government revenue in a given period"},
        ],
        "content_md": r"""## The functions of money

Money serves four main functions: a medium of exchange (avoids the need for direct barter), a unit of account (a common way to measure and compare the value of different goods), a store of value (can be saved and used later), and a standard of deferred payment (allows debts and future payments to be agreed in fixed terms).

## The banking system

A central bank (like the Central Bank of Nigeria) regulates the country's money supply, sets monetary policy, and oversees commercial banks -- it does not deal directly with the general public. Commercial banks accept deposits from and lend money to individuals and businesses, earning interest on loans while paying a smaller interest rate on deposits.

## Taxation

A direct tax is paid straight to the government by the person or organization it's charged on, based on their income or wealth (e.g. personal income tax, company tax). An indirect tax is added to the price of goods/services and collected by sellers on the government's behalf (e.g. Value Added Tax).

Example 1: Classify personal income tax and VAT as direct or indirect taxes, and explain the difference.
Personal income tax is a direct tax -- it's paid straight to the government by the earner, based on their income. VAT is an indirect tax -- it's added to the price of goods and collected by the seller, who then remits it to the government; the tax burden falls on whoever buys the good, not on a specific named taxpayer.

## Government budgets

A government budget deficit occurs when spending exceeds revenue in a period, usually financed by borrowing. A budget surplus occurs when revenue exceeds spending. Persistent deficits can lead to rising government debt, which is why governments often aim for a balanced budget or manageable deficit over time.""",
        "related_topics": ["National Income and Economic Planning", "Business Organisation and Government"],
    },
    {
        "subject": "Economics",
        "topic": "National Income and Economic Planning",
        "title": "National Income and Economic Planning",
        "summary": "How national income is measured, the circular flow of income, and why countries use economic development plans.",
        "glossary": [
            {"term": "Gross Domestic Product (GDP)", "definition": "the total value of all goods and services produced within a country's borders in a given period"},
            {"term": "Gross National Product (GNP)", "definition": "GDP plus income earned by citizens abroad, minus income earned domestically by foreigners"},
            {"term": "Circular flow of income", "definition": "a model showing how money flows between households and firms through spending, income, and factor payments"},
            {"term": "Economic planning", "definition": "a government's deliberate strategy for directing a country's economic development over a set period"},
        ],
        "content_md": r"""## Measuring national income

GDP measures the total value of all goods and services produced within a country's borders, regardless of who owns the producing businesses. GNP adjusts this to measure income earned by that country's citizens/residents, wherever in the world they earned it, adding income earned abroad and subtracting income foreigners earned domestically.

Example 1: A country's GDP is ₦50 trillion. Its citizens earn ₦2 trillion from investments abroad, and foreigners earn ₦3 trillion from investments within the country. Find the country's GNP.
\(GNP = GDP + \text{income earned abroad by citizens} - \text{income earned domestically by foreigners} = 50 + 2 - 3 = 49\) trillion naira.

## The circular flow of income

In its simplest form, households supply factors of production (land, labour, capital) to firms and receive income (rent, wages, interest, profit) in return; firms use these factors to produce goods and services, which households buy using that income, spending flows back to firms. This continuous cycle links income, spending, and production across the economy.

## Economic planning

Economic planning involves a government setting deliberate goals and strategies for national development over a period -- for example, targets for infrastructure, industrialization, or poverty reduction -- and coordinating policies (spending, taxation, regulation) to work towards them, rather than leaving all outcomes purely to market forces.""",
        "related_topics": ["Money, Banking, and Public Finance", "Population and Statistics"],
    },
    {
        "subject": "Economics",
        "topic": "International Trade",
        "title": "International Trade",
        "summary": "Why countries trade with each other, common trade barriers, and the basics of exchange rates and the balance of payments.",
        "glossary": [
            {"term": "Comparative advantage", "definition": "a country's ability to produce a good at a lower opportunity cost than another country, the basis for beneficial trade"},
            {"term": "Tariff", "definition": "a tax placed on imported goods to make them more expensive relative to domestic goods"},
            {"term": "Quota", "definition": "a limit on the quantity of a good that can be imported in a given period"},
            {"term": "Exchange rate", "definition": "the price of one country's currency in terms of another"},
            {"term": "Balance of payments", "definition": "a record of all economic transactions between a country's residents and the rest of the world"},
        ],
        "content_md": r"""## Why countries trade

Countries trade because they have different resources, skills, and climates, making some better suited to producing certain goods than others. The theory of comparative advantage says a country benefits from specializing in producing goods it can make at a lower opportunity cost than other countries, and trading for the rest -- even if another country could produce everything more efficiently in absolute terms.

Example 1: Country A can produce either 10 units of cocoa or 5 units of cloth with its resources; Country B can produce either 6 units of cocoa or 6 units of cloth with the same resources. Which good should Country A specialize in?
Country A's opportunity cost of 1 unit of cocoa is 0.5 units of cloth given up, while Country B's opportunity cost of 1 unit of cocoa is 1 unit of cloth given up. Country A has the lower opportunity cost for cocoa, so it has a comparative advantage in cocoa and should specialize in producing it, trading with Country B for cloth.

## Trade barriers

A tariff is a tax on imports, making foreign goods more expensive and protecting domestic producers from foreign competition. A quota directly limits how much of a good can be imported, regardless of price. Both barriers protect domestic industries but tend to raise prices for consumers and can invite retaliation from trading partners.

## Exchange rates and balance of payments

The exchange rate determines how much of one currency is needed to buy another; it affects the relative price of a country's exports and imports. The balance of payments records all transactions between a country and the rest of the world, including trade in goods and services, investment flows, and transfers -- a useful summary of a country's overall economic relationship with the rest of the world.""",
        "related_topics": ["Demand, Supply, and Market Structures", "National Income and Economic Planning"],
    },
    {
        "subject": "Economics",
        "topic": "Population and Statistics",
        "title": "Population and Statistics",
        "summary": "Key population concepts used in economics, and basic statistical tools like the mean and index numbers.",
        "glossary": [
            {"term": "Census", "definition": "an official count of a country's population, usually including demographic details"},
            {"term": "Population growth rate", "definition": "the rate at which a population increases (or decreases) over a period, usually expressed as a percentage per year"},
            {"term": "Mean (average)", "definition": "the sum of a set of values divided by how many values there are"},
            {"term": "Index number", "definition": "a figure showing how a variable (like prices) has changed relative to a fixed base value, usually set at 100"},
        ],
        "content_md": r"""## Population concepts

A census is an official count of a country's population, often collecting details like age, sex, and occupation, and is essential for economic planning (e.g. estimating demand for schools, hospitals, and jobs). Population growth rate measures how fast a population is changing, driven by birth rates, death rates, and net migration.

Example 1: A country's population grows from 40 million to 42 million in one year. Find its population growth rate.
Growth rate = \(\dfrac{\text{change in population}}{\text{original population}} \times 100 = \dfrac{2}{40} \times 100 = 5\%\).

## Basic statistical measures

The mean (average) of a data set is found by adding all the values and dividing by the number of values.

Example 2: Find the mean of the following weekly incomes: ₦5,000, ₦7,000, ₦6,000, ₦8,000.
Mean = \(\dfrac{5{,}000 + 7{,}000 + 6{,}000 + 8{,}000}{4} = \dfrac{26{,}000}{4} = 6{,}500\) naira.

## Index numbers

An index number expresses a value relative to a fixed base period, usually set to 100, making it easy to see percentage changes over time. A common example is a price index, which tracks how the general price level has changed since the base year -- if a price index rises from 100 to 115, average prices have risen by 15% since the base year.""",
        "related_topics": ["National Income and Economic Planning", "Demand, Supply, and Market Structures"],
    },
    {
        "subject": "Economics",
        "topic": "Theory of Consumer Behaviour",
        "title": "Theory of Consumer Behaviour",
        "summary": "How consumers make choices to maximize satisfaction, and the law of diminishing marginal utility.",
        "glossary": [
            {"term": "Utility", "definition": "the satisfaction or benefit a consumer gets from consuming a good or service"},
            {"term": "Marginal utility", "definition": "the extra satisfaction gained from consuming one additional unit of a good"},
            {"term": "Law of diminishing marginal utility", "definition": "as a consumer consumes more units of a good, the extra satisfaction from each additional unit tends to fall"},
        ],
        "content_md": r"""## Utility and consumer choice

Utility is the satisfaction a consumer gets from consuming a good. Consumers aim to get the most total utility possible from their limited income, which is why they typically spread spending across different goods rather than buying only one thing.

## The law of diminishing marginal utility

As a person consumes more units of the same good in a given period, the additional satisfaction (marginal utility) from each extra unit tends to decrease -- the first unit of something is usually worth more to you than the tenth.

Example 1: A student eats plates of rice one after another. The first plate gives high satisfaction; by the fourth plate, they feel little extra enjoyment and are close to full. Explain this using the law of diminishing marginal utility.
This illustrates diminishing marginal utility -- the extra (marginal) satisfaction from each additional plate of rice falls as more plates are consumed, since the student's need/desire for rice is progressively satisfied, until the extra utility from another plate becomes very small.

## Consumer equilibrium

A rational consumer with a fixed income and multiple goods to choose from reaches "consumer equilibrium" -- the spending combination that maximizes their total utility -- when the marginal utility gained per naira spent is equal across all the goods they buy. If one good gives more satisfaction per naira than another, a rational consumer would shift spending towards it until the balance evens out.""",
        "related_topics": ["Demand, Supply, and Market Structures", "Basic Economic Concepts and Systems"],
    },
    {
        "subject": "Economics",
        "topic": "Business Organisation and Government",
        "title": "Business Organisation and Government",
        "summary": "The main forms of business ownership, and the role of public enterprises and privatization in the economy.",
        "glossary": [
            {"term": "Sole proprietorship", "definition": "a business owned and run by one person, who has unlimited liability for its debts"},
            {"term": "Partnership", "definition": "a business owned by two or more people who share management, profits, and liability"},
            {"term": "Limited liability company", "definition": "a business whose owners (shareholders) are only liable for company debts up to the amount they invested"},
            {"term": "Privatization", "definition": "the transfer of ownership of a business or industry from government to private investors"},
        ],
        "content_md": r"""## Forms of business organization

A sole proprietorship is owned by one person, who makes all decisions and keeps all profits, but also bears unlimited personal liability for the business's debts. A partnership is owned by two or more people who share capital, management, profits, and liability, allowing more resources and shared expertise than a sole proprietorship, but with the risk of disagreements between partners. A limited liability company is owned by shareholders, who are only liable up to the amount they've invested (limited liability), making it easier to raise large amounts of capital, though it involves more regulation and reporting requirements.

Example 1: Explain one advantage a limited liability company has over a sole proprietorship when it comes to raising capital.
A limited liability company can raise capital by selling shares to many investors, who are attracted by the protection of limited liability (they can only lose what they invested) -- giving access to far more potential capital than a sole proprietorship, which typically relies only on the owner's personal funds and loans.

## Public enterprises and privatization

A public enterprise is a business owned and run by the government, often in sectors seen as essential (like utilities) or requiring large capital investment. Privatization is the process of transferring ownership of such enterprises to private investors, often pursued to improve efficiency, reduce government spending burdens, and encourage competition -- though it can also raise concerns about access and pricing for essential services once profit becomes the primary motive.""",
        "related_topics": ["Basic Economic Concepts and Systems", "Money, Banking, and Public Finance"],
    },
    {
        "subject": "Economics",
        "topic": "Agriculture, Industry, and Petroleum Economics",
        "title": "Agriculture, Industry, and Petroleum Economics",
        "summary": "Agriculture's role in the Nigerian economy, challenges facing industrialization, and the risks of depending heavily on petroleum.",
        "glossary": [
            {"term": "Subsistence agriculture", "definition": "farming mainly to feed the farmer's own family, with little surplus sold for profit"},
            {"term": "Industrialization", "definition": "the process of developing a country's manufacturing and industrial sectors"},
            {"term": "Mono-economy", "definition": "an economy that depends heavily on a single sector or export for most of its revenue"},
            {"term": "Economic diversification", "definition": "developing multiple sectors of an economy, to reduce dependence on any single one"},
        ],
        "content_md": r"""## Agriculture's role in the Nigerian economy

Agriculture employs a large share of Nigeria's workforce and remains central to food security and rural livelihoods, even though its share of GDP has fallen relative to the oil sector. Much of Nigerian agriculture is still subsistence-based (farming mainly to feed one's own family), though commercial/cash-crop farming (cocoa, rubber, palm oil) also plays an important export role.

## Challenges facing industrialization in Nigeria

Nigerian industrialization faces several persistent challenges: inadequate power supply (raising production costs and unreliability), poor transport infrastructure (raising costs of moving goods), limited access to affordable credit/capital for businesses, and competition from cheaper imported manufactured goods.

Example 1: Explain how unreliable electricity supply raises production costs for a Nigerian manufacturing business.
When public electricity supply is unreliable, manufacturers must rely on generators for backup power, which cost more per unit of electricity produced (fuel, maintenance) than grid power would. These extra costs get built into the price of the finished goods, making the manufacturer less price-competitive, especially against imported alternatives from countries with more reliable, cheaper power.

## The petroleum sector and economic diversification

Nigeria's economy has long depended heavily on petroleum for export earnings and government revenue, making it a mono-economy vulnerable to swings in global oil prices -- a sharp drop in oil prices can severely strain government budgets and foreign exchange earnings. Economic diversification -- deliberately growing other sectors like agriculture, manufacturing, technology, and services -- aims to reduce this vulnerability and build more stable, broad-based economic growth.""",
        "related_topics": ["Theory of Production and Distribution", "International Trade"],
    },
    {
        "subject": "Literature",
        "topic": "Literary Devices/Terminology",
        "title": "Literary Devices and Terminology",
        "summary": "The figures of speech and literary terms examiners expect you to name and explain -- with examples of each.",
        "glossary": [
            {"term": "Simile", "definition": "a comparison between two unlike things using \"like\" or \"as\", e.g. \"brave as a lion\""},
            {"term": "Metaphor", "definition": "a direct comparison between two unlike things without \"like\" or \"as\", e.g. \"time is a thief\""},
            {"term": "Personification", "definition": "giving human qualities or actions to a non-human thing, e.g. \"the wind whispered\""},
            {"term": "Irony", "definition": "a contrast between what is expected/said and what actually happens or is meant"},
            {"term": "Symbolism", "definition": "using an object, person, or action to represent a deeper idea beyond its literal meaning"},
        ],
        "content_md": r"""## Figures of comparison

A simile compares two unlike things using "like" or "as": "her smile was like sunshine." A metaphor makes the same kind of comparison but states it directly, without "like" or "as": "her smile was sunshine." Personification gives human qualities to something non-human: "the old house groaned in the storm."

Example 1: Identify the figure of speech in "Grief is a heavy stone I carry everywhere," and explain your answer.
This is a metaphor -- grief is directly described as being a stone, with no "like" or "as" used, making a direct comparison rather than a similarity-based one.

## Sound devices

Alliteration repeats the same starting consonant sound in nearby words: "the wild wind whistled." Assonance repeats vowel sounds within nearby words: "the rain in Spain." Onomatopoeia uses words that imitate the sound they describe: "buzz," "crash," "sizzle."

Example 2: Identify the sound device in "the busy bees buzzed by the blooming bush," and explain your answer.
This is alliteration -- the repeated "b" sound at the start of several nearby words ("busy," "bees," "buzzed," "by," "blooming," "bush") creates the rhythmic, repeated-consonant effect.

## Other common devices

Irony creates a gap between expectation and reality -- a firefighter's house burning down is situational irony; a character confidently walking into danger they don't see (but the audience does) is dramatic irony. Symbolism uses a concrete object or image to represent an abstract idea, like a dove symbolizing peace, or a wilting flower symbolizing lost innocence. Hyperbole is deliberate exaggeration for effect: "I've told you a million times."

Example 3: A story describes a caged bird singing beautifully despite never having known freedom. What might the caged bird symbolize?
The caged bird could symbolize resilience or hope despite oppression/confinement -- the ability to find and express beauty or joy even within restricted circumstances is a common symbolic reading of this image across literature.""",
        "related_topics": ["General Literary Principles", "Literary Appreciation"],
    },
    {
        "subject": "Literature",
        "topic": "Drama Set Texts",
        "title": "Drama Set Texts",
        "summary": "How to study any prescribed play systematically -- plot structure, characterization, and the kinds of questions drama set texts are examined on. Your specific set play changes each exam cycle, so pair this with a close reading of your own assigned text.",
        "glossary": [
            {"term": "Plot", "definition": "the sequence of events that make up a story, usually built around a central conflict"},
            {"term": "Characterization", "definition": "the methods a writer uses to create and reveal a character's personality"},
            {"term": "Dramatic irony", "definition": "when the audience knows something a character on stage does not"},
            {"term": "Stage direction", "definition": "an instruction in a play's text describing how it should be performed, e.g. movement, tone, setting"},
            {"term": "Climax", "definition": "the turning point of a play, where tension reaches its peak"},
        ],
        "content_md": r"""## How to study your prescribed drama text

This note covers general skills -- your actual exam will be based on a specific play chosen for that year, so this is not a substitute for reading your assigned text closely. Read the full play at least twice: once for the overall story, and again noting act/scene divisions, key turning points, and each major character's role. Keep brief notes on each character's motivations and how they change (or don't) across the play.

## Plot structure

Most plays follow a recognizable shape: exposition (introducing characters, setting, and the initial situation), rising action (a conflict develops and intensifies), climax (the turning point, where tension peaks), falling action (consequences of the climax unfold), and resolution (the conflict is settled, for better or worse).

Example 1: A play opens by introducing a king and his loyal advisor, then reveals the advisor is secretly plotting against him. Which part of the plot structure does this represent?
This is the exposition combined with the start of rising action -- the opening establishes the characters and setting (exposition), while the revealed secret plot immediately introduces the central conflict that will drive the rising tension through the rest of the play.

## Characterization

Playwrights reveal character through what characters say (dialogue), what they do (action), what others say about them, and sometimes direct stage directions describing their manner. Look for contradictions between what a character claims and what they actually do -- these often reveal deeper truths about them.

## Answering drama questions in the exam

Common question types include: character analysis ("Discuss X's role in the play"), theme questions ("What does the play say about power/ambition/betrayal?"), and significance questions ("Discuss the importance of a particular scene"). Always support your points with specific references to what happens in the play -- named characters, specific events, and (where you can recall them) actual lines -- rather than vague generalizations.""",
        "related_topics": ["General Literary Principles", "Literary Devices/Terminology"],
    },
    {
        "subject": "Literature",
        "topic": "Prose Set Texts",
        "title": "Prose Set Texts",
        "summary": "How to study any prescribed novel systematically -- narrative point of view, characters, and themes. Your specific set novel changes each exam cycle, so pair this with a close reading of your own assigned text.",
        "glossary": [
            {"term": "Narrator", "definition": "the voice telling the story -- may or may not be a character within it"},
            {"term": "Point of view", "definition": "the perspective from which a story is told, e.g. first-person or third-person"},
            {"term": "Protagonist", "definition": "the main character a story centres around"},
            {"term": "Theme", "definition": "a central idea or message explored throughout a work"},
            {"term": "Motif", "definition": "a recurring image, idea, or symbol that reinforces a work's central themes"},
        ],
        "content_md": r"""## How to study your prescribed novel

This note covers general skills -- your actual exam will be based on a specific novel chosen for that year, so this is not a substitute for reading your assigned text closely. Read the novel fully at least once for the story, then a second time taking notes chapter by chapter on major events, and how each main character develops.

## Narrative point of view

A first-person narrator ("I") is a character within the story, so we only know what they know or notice -- their account can be biased or limited. A third-person narrator is outside the story; "third-person omniscient" knows every character's thoughts, while "third-person limited" follows just one character's perspective closely.

Example 1: A novel is narrated by a young girl who describes events as she experiences them, sometimes misunderstanding adult conversations happening around her. Identify the point of view and explain one effect of this choice.
This is first-person narration. One effect is that the reader's understanding is limited to what the young narrator notices and correctly interprets -- creating gaps or misunderstandings that the reader may see through even when the narrator doesn't, adding irony or poignancy to the story.

## Characters and themes

The protagonist is the character the story centres around, though not always a purely "good" character. Look for how the protagonist changes (or fails to change) by the story's end, and what obstacles (internal or external) they face. A theme is a central idea the whole novel explores -- like ambition, betrayal, identity, or the effects of colonialism -- often revealed through repeated situations, symbols (motifs), or the consequences characters face for their choices.

## Answering prose questions in the exam

Common question types include: character analysis, theme discussion, and questions about narrative technique or a specific passage's significance. As with drama, always ground your answer in specific details from the novel -- named characters, events, and their consequences -- rather than general statements that could apply to any story.""",
        "related_topics": ["General Literary Principles", "Literary Appreciation"],
    },
    {
        "subject": "Literature",
        "topic": "Poetry Set Texts",
        "title": "Poetry Set Texts",
        "summary": "How to analyze any prescribed poem -- structure, rhyme scheme, tone, and imagery. Your specific set poems change each exam cycle, so pair this with a close reading of your own assigned texts.",
        "glossary": [
            {"term": "Stanza", "definition": "a grouped set of lines in a poem, similar to a paragraph in prose"},
            {"term": "Rhyme scheme", "definition": "the pattern of rhyming line-endings in a poem, described with letters, e.g. ABAB"},
            {"term": "Tone", "definition": "the poet's attitude towards the subject, conveyed through word choice and style"},
            {"term": "Imagery", "definition": "descriptive language that appeals to the senses, creating vivid mental pictures"},
            {"term": "Persona", "definition": "the voice or character speaking in a poem, who may or may not be the poet themselves"},
        ],
        "content_md": r"""## How to study your prescribed poems

This note covers general skills -- your actual exam will be based on specific poems chosen for that year, so this is not a substitute for close, repeated reading of your assigned poems. Read each poem aloud at least once -- rhythm and sound patterns are often easier to notice by ear than by eye. Note the poem's structure (stanza count and length), and identify who is "speaking" (the persona), since this shapes how the whole poem should be read.

## Rhyme scheme

Rhyme scheme is described by assigning a letter to each line-ending sound, with matching letters for lines that rhyme.

Example 1: Identify the rhyme scheme of a four-line stanza where lines 1 and 3 rhyme, and lines 2 and 4 rhyme.
This is an ABAB rhyme scheme -- line 1 (A) rhymes with line 3 (A), and line 2 (B) rhymes with line 4 (B), alternating throughout the stanza.

## Tone and imagery

Tone is the poet's (or persona's) attitude towards the subject -- mournful, celebratory, bitter, nostalgic, playful -- shown through word choice, rhythm, and imagery, not stated directly. Imagery uses descriptive, sensory language (sight, sound, touch, smell, taste) to create vivid mental pictures that reinforce the poem's mood and meaning.

Example 2: A poem describes "grey clouds pressing low over silent, empty streets." What tone does this imagery suggest?
This imagery suggests a bleak, sombre, or melancholic tone -- the grey colour, the "pressing" weight of the clouds, and the silence and emptiness of the streets all combine to create a heavy, gloomy atmosphere rather than a cheerful or hopeful one.

## Answering poetry questions in the exam

Common question types include: identifying and explaining literary devices used, discussing the poem's theme or message, analyzing tone or mood, and comparing two poems' treatment of a similar subject. Always quote or closely reference specific words/lines to support your points.""",
        "related_topics": ["Literary Devices/Terminology", "Literary Appreciation"],
    },
    {
        "subject": "Literature",
        "topic": "General Literary Principles",
        "title": "General Literary Principles",
        "summary": "The three genres of literature, what literature is generally understood to do, and how context shapes a text's meaning.",
        "glossary": [
            {"term": "Genre", "definition": "a category of literary work, e.g. prose, drama, or poetry, each with characteristic forms and conventions"},
            {"term": "Prose", "definition": "written or spoken language in its ordinary form, without a regular poetic structure -- novels and short stories"},
            {"term": "Setting", "definition": "the time and place in which a story's events occur"},
            {"term": "Context", "definition": "the historical, social, or cultural background that shapes a text's meaning"},
        ],
        "content_md": r"""## The three genres of literature

Prose is written in ordinary sentence and paragraph form -- novels and short stories are the main prose forms studied. Drama is written to be performed, structured through dialogue and stage directions, organized into acts and scenes. Poetry uses condensed, often rhythmic or rhymed language, structured into lines and stanzas, to convey meaning and feeling efficiently.

## Functions of literature

Literature can entertain (tell an engaging story), educate (teach a lesson or convey knowledge), and reflect or critique society (holding up real social issues, values, or events for examination through a fictional lens). A single work often does more than one of these at once -- a highly entertaining story can still carry a serious social message.

## Context and its importance

A text's historical, social, or cultural context often shapes its meaning significantly. Understanding when and where a work was written (or set) -- what social norms, conflicts, or events were happening -- helps explain characters' choices and a work's underlying themes, which might otherwise seem puzzling to a modern reader unfamiliar with that background.

Example 1: A novel written during a period of colonial rule portrays a native character who is torn between traditional customs and newly introduced foreign values. Why is understanding the historical context important here?
Understanding the colonial-era setting explains why this internal conflict exists in the first place -- the pressure to abandon or blend traditional practices with imposed foreign systems was a real, common experience during colonial rule, and this context helps a reader see the character's struggle as representative of a broader social tension, not just a personal quirk.""",
        "related_topics": ["Literary Appreciation", "Literary Devices/Terminology"],
    },
    {
        "subject": "Literature",
        "topic": "Literary Appreciation",
        "title": "Literary Appreciation",
        "summary": "How to critically analyze a writer's style and form an informed judgement about how effectively a text achieves its purpose.",
        "glossary": [
            {"term": "Critical analysis", "definition": "a close, evaluative examination of how a text works and how effectively it achieves its purpose"},
            {"term": "Style", "definition": "a writer's distinctive way of using language -- word choice, sentence structure, tone, and devices"},
            {"term": "Diction", "definition": "a writer's specific choice of words, which shapes tone and meaning"},
        ],
        "content_md": r"""## What literary appreciation means

Literary appreciation goes beyond summarizing what happens in a text -- it means evaluating how a writer achieves their effects, and forming a supported judgement about how successfully they do so. This means paying close attention to specific choices of language, structure, and technique, not just plot events.

## Analyzing style and diction

A writer's diction (word choice) strongly shapes tone -- formal versus casual words, harsh versus gentle sounding words, simple versus elaborate vocabulary, all create different effects even when describing the same basic event. Sentence structure matters too: short, blunt sentences can create tension or urgency, while long, flowing sentences can create a reflective or calm mood.

Example 1: Compare the effect of describing a storm as "the wind grew a little stronger, and rain began to fall" versus "the wind howled and screamed, hurling sheets of rain against the trembling windows."
The first description uses plain, neutral diction and a calm sentence structure, creating a mild, almost unremarkable tone. The second uses vivid, violent verbs ("howled," "screamed," "hurling") and personification, creating a dramatic, threatening tone -- the same basic event (a storm) is made to feel far more intense purely through word choice and style.

## Forming a critical opinion

A strong literary appreciation answer doesn't just describe what a device or technique is -- it explains why the writer likely chose it, and evaluates how effectively it serves the text's overall purpose or theme. Always back up judgements ("this is effective because...") with specific evidence from the text, rather than offering opinions without support.""",
        "related_topics": ["Literary Devices/Terminology", "General Literary Principles"],
    },
    {
        "subject": "Government",
        "topic": "Systems of Government",
        "title": "Systems of Government",
        "summary": "Unitary vs federal systems, presidential vs parliamentary government, and the separation of powers.",
        "glossary": [
            {"term": "Unitary system", "definition": "a system where all governing power is concentrated in a single central government"},
            {"term": "Federal system", "definition": "a system where power is constitutionally divided between a central government and regional/state governments"},
            {"term": "Presidential system", "definition": "a system where the head of state/government is directly elected and separate from the legislature, e.g. the USA and Nigeria"},
            {"term": "Parliamentary system", "definition": "a system where the executive is drawn from and accountable to the legislature, e.g. the UK"},
            {"term": "Separation of powers", "definition": "dividing government functions among the executive, legislature, and judiciary, each acting as a check on the others"},
        ],
        "content_md": r"""## Unitary vs federal systems

In a unitary system, all significant governing power rests with the central government, which may delegate some administrative functions to local bodies but can revoke that delegation. In a federal system, power is constitutionally divided between a central (federal) government and constituent states/regions, each with their own guaranteed areas of authority that the centre cannot simply override.

Example 1: Nigeria has 36 states, each with its own governor, House of Assembly, and defined powers alongside the federal government. Which system does this describe?
This describes a federal system -- power is constitutionally shared between the federal government and the states, each with defined areas of authority, rather than all power being concentrated centrally as in a unitary system.

## Presidential vs parliamentary systems

In a presidential system, the head of state and head of government (often the same person, the president) is elected separately from the legislature and serves a fixed term, largely independent of the legislature's day-to-day confidence. In a parliamentary system, the executive (prime minister and cabinet) is drawn from the legislature (parliament) and remains in office only as long as it retains the legislature's confidence/support.

## Separation of powers

Government functions are typically divided into three branches: the executive (implements and enforces laws), the legislature (makes laws), and the judiciary (interprets laws and settles disputes). Separating these functions, with each branch able to check the others' power, helps prevent any single branch from becoming too powerful.""",
        "related_topics": ["Constitutional Government", "Comparative Government"],
    },
    {
        "subject": "Government",
        "topic": "Constitutional Government",
        "title": "Constitutional Government",
        "summary": "What a constitution does, the different types of constitutions, and the principles of rule of law and fundamental human rights.",
        "glossary": [
            {"term": "Constitution", "definition": "the fundamental set of principles and rules that establishes how a state is governed"},
            {"term": "Rule of law", "definition": "the principle that everyone, including government, is subject to and accountable under the law"},
            {"term": "Fundamental human rights", "definition": "basic rights and freedoms guaranteed to every citizen, often protected by the constitution"},
            {"term": "Rigid constitution", "definition": "a constitution that requires a special, difficult procedure to amend"},
            {"term": "Flexible constitution", "definition": "a constitution that can be amended through the ordinary legislative process"},
        ],
        "content_md": r"""## What a constitution does

A constitution establishes how a country is governed -- defining the structure of government, the powers and limits of each branch, the relationship between different levels of government, and (usually) the rights guaranteed to citizens. It serves as the supreme law, meaning ordinary laws that conflict with it can be struck down.

## Types of constitutions

A written constitution exists as a single, formal document (like Nigeria's or the USA's); an unwritten constitution is built from various sources -- statutes, conventions, court decisions -- without one consolidated document (like the UK's). A rigid constitution requires a special, more difficult procedure to amend (often a supermajority vote or referendum); a flexible constitution can be changed through the ordinary law-making process.

Example 1: Nigeria's 1999 Constitution requires approval by two-thirds of both houses of the National Assembly and a majority of State Houses of Assembly to amend it. Is this a rigid or flexible constitution?
This is a rigid constitution -- amending it requires a special, demanding procedure well beyond passing an ordinary law, deliberately making changes harder than routine legislation.

## Rule of law and constitutionalism

The rule of law means no one, including government officials, is above the law -- everyone is equally subject to it and accountable through the courts. Constitutionalism is the broader idea that government power should be limited and exercised according to established constitutional rules, not the arbitrary will of whoever holds power.

## Fundamental human rights

Most constitutions guarantee certain basic rights to citizens, such as freedom of speech, freedom of association, the right to a fair hearing, and freedom from discrimination. These rights limit what government can legally do to individuals, and citizens can typically challenge violations of these rights in court.""",
        "related_topics": ["Systems of Government", "Political Concepts/Theory"],
    },
    {
        "subject": "Government",
        "topic": "Electoral Systems",
        "title": "Electoral Systems",
        "summary": "The main methods of electing representatives, universal adult suffrage, and the stages of a typical electoral process.",
        "glossary": [
            {"term": "Suffrage", "definition": "the right to vote in elections"},
            {"term": "Electorate", "definition": "the body of people entitled to vote in an election"},
            {"term": "First-past-the-post", "definition": "an electoral system where the candidate with the most votes in a constituency wins, even without a majority"},
            {"term": "Proportional representation", "definition": "an electoral system where seats are allocated to parties in proportion to the votes they receive"},
        ],
        "content_md": r"""## Methods of election

First-past-the-post (FPTP) divides a country into constituencies, and in each one, the candidate with the most votes wins the seat -- even if they don't win an outright majority. Proportional representation (PR) allocates seats to parties roughly in proportion to their overall share of the vote, so a party winning 30% of the national vote gets roughly 30% of the seats.

Example 1: In a constituency, Candidate A gets 40% of the vote, Candidate B gets 35%, and Candidate C gets 25%. Under first-past-the-post, who wins the seat?
Candidate A wins -- FPTP awards the seat to whoever gets the most votes, regardless of whether that's an outright majority (more than 50%). Candidate A's 40% is the largest share here, even though 60% of voters chose someone else.

## Universal adult suffrage

Universal adult suffrage means every adult citizen (typically 18 years and above) has the right to vote, regardless of gender, ethnicity, religion, or wealth -- a principle most modern democracies, including Nigeria, are constitutionally committed to, though it took long historical struggles in many countries to achieve.

## The electoral process

A typical election process includes voter registration (compiling the electorate), campaigning (candidates and parties present their case to voters), the actual voting, and collation (counting and combining results from different polling units into a final result). Independent electoral bodies (like Nigeria's INEC) are usually responsible for organizing and overseeing this process to ensure it's conducted fairly.""",
        "related_topics": ["Political Parties/Pressure Groups", "Nigerian Government/Politics"],
    },
    {
        "subject": "Government",
        "topic": "Political Concepts/Theory",
        "title": "Political Concepts and Theory",
        "summary": "Core political concepts -- sovereignty, power versus authority, legitimacy -- and the main forms government can take.",
        "glossary": [
            {"term": "Sovereignty", "definition": "the supreme, independent authority of a state to govern itself without external control"},
            {"term": "Power", "definition": "the ability to influence or control others' behaviour, with or without their consent"},
            {"term": "Authority", "definition": "power that is recognized as legitimate and rightful by those subject to it"},
            {"term": "Legitimacy", "definition": "the recognized right of a government to rule, usually based on law, tradition, or popular consent"},
            {"term": "Democracy", "definition": "a system of government in which power is held by the people, directly or through elected representatives"},
        ],
        "content_md": r"""## Sovereignty

Sovereignty is a state's supreme authority to govern itself, free from external control -- both internally (having the final say over its own laws and affairs) and externally (recognized as independent by other states in the international system).

## Power vs authority

Power is simply the ability to make others act a certain way, whether or not they accept it as right (e.g. a dictator ruling through fear still holds power). Authority is power that is seen as legitimate and rightful by those subject to it -- people obey not just out of fear, but because they accept the ruler's right to command.

Example 1: A newly installed military ruler forces compliance through the threat of the army, but citizens widely see the takeover as illegal and resent the regime. Does this ruler have power, authority, or both?
This ruler has power (the ability to enforce compliance through force) but lacks authority, since citizens do not recognize the takeover as legitimate or rightful -- illustrating that power and authority, while often found together, are not the same thing.

## Forms of government

A democracy places power in the hands of the people, either directly or through elected representatives, typically with regular free elections, protected rights, and government accountability. An autocracy concentrates power in a single ruler or small group with little accountability to the wider population. A totalitarian government goes further, seeking to control nearly all aspects of public and private life, often suppressing opposition and dissent entirely.""",
        "related_topics": ["Constitutional Government", "Systems of Government"],
    },
    {
        "subject": "Government",
        "topic": "International Relations",
        "title": "International Relations",
        "summary": "Diplomacy and foreign policy, the role of international organizations, and the basics of treaties.",
        "glossary": [
            {"term": "Diplomacy", "definition": "the management of relationships between states through negotiation and communication, rather than force"},
            {"term": "Foreign policy", "definition": "a country's strategy for managing its relationships and interests with other states"},
            {"term": "Treaty", "definition": "a formal, legally binding agreement between two or more states"},
        ],
        "content_md": r"""## Diplomacy and foreign policy

Diplomacy is how states manage relationships with each other -- negotiation, communication, and representation -- as an alternative to conflict. A country's foreign policy sets out its goals and strategies for these relationships, shaped by its national interests: security, economic gain, and international influence or standing.

## International organizations

The United Nations (UN) is the main global organization for cooperation on peace, security, and development among its member states. The African Union (AU) promotes political and economic cooperation and integration among African states. ECOWAS focuses specifically on economic integration and cooperation among West African states, including free movement across member states' borders.

Example 1: Explain one key function of the United Nations.
One key function is maintaining international peace and security -- for example, through peacekeeping missions, mediating disputes between member states, and providing a forum where countries can raise and discuss conflicts before they escalate into wider wars.

## Treaties

A treaty is a formal, legally binding agreement between states, covering areas like trade, defence, borders, or environmental cooperation. Once ratified according to each country's own constitutional process, a treaty creates binding obligations under international law, though enforcement ultimately depends on states' willingness to comply, since there's no single global authority that can force compliance the way a national government can enforce domestic law.""",
        "related_topics": ["Comparative Government", "Nigerian Government/Politics"],
    },
    {
        "subject": "Government",
        "topic": "Nigerian Government/Politics",
        "title": "Nigerian Government and Politics",
        "summary": "Nigeria's constitutional development since independence, and the current structure of its federal government.",
        "glossary": [
            {"term": "Federal character principle", "definition": "a constitutional requirement that government appointments/composition reflect Nigeria's diverse states and ethnic groups"},
            {"term": "National Assembly", "definition": "Nigeria's federal legislature, made up of the Senate and the House of Representatives"},
            {"term": "Republic", "definition": "a state where the head of state is not a hereditary monarch, typically an elected or appointed president"},
        ],
        "content_md": r"""## Nigeria's constitutional development

Nigeria gained independence from British colonial rule in 1960, initially as a parliamentary system under a constitutional monarchy (with the British monarch as head of state). Nigeria became a republic in 1963, with its own president as head of state. After periods of military rule, Nigeria adopted a presidential system of government under the 1979 Constitution, which (after further military interruptions) was followed by the current 1999 Constitution, marking the return to civilian, democratic rule that continues today.

## Structure of Nigeria's government

Nigeria's federal government has three arms: the executive (headed by the President), the legislature (the bicameral National Assembly, made up of the Senate and House of Representatives), and the judiciary (headed by the Supreme Court). Power is federally divided between the central government and the 36 states, each with its own governor and House of Assembly.

Example 1: Explain the purpose of Nigeria's federal character principle.
The federal character principle requires that appointments to public offices and the composition of government bodies reflect Nigeria's diverse states and ethnic groups, aiming to prevent any single group from dominating government and to promote national unity and a sense of fair representation across Nigeria's many different communities.""",
        "related_topics": ["Systems of Government", "Local Government"],
    },
    {
        "subject": "Government",
        "topic": "Political Parties/Pressure Groups",
        "title": "Political Parties and Pressure Groups",
        "summary": "The functions of political parties, how they differ from pressure groups, and the main types of party systems.",
        "glossary": [
            {"term": "Political party", "definition": "an organized group that seeks to gain and exercise government power by contesting elections"},
            {"term": "Pressure group", "definition": "an organized group that seeks to influence government policy without itself seeking to hold government power"},
            {"term": "One-party system", "definition": "a political system where only one political party is legally permitted to hold power"},
            {"term": "Multi-party system", "definition": "a political system where several political parties genuinely compete for power"},
        ],
        "content_md": r"""## Functions of political parties

Political parties select and present candidates for election, develop policy platforms/manifestos, mobilize and educate voters, and (once in power) form the government and take responsibility for governing -- or, if not in power, act as an organized opposition holding the government accountable.

## Political parties vs pressure groups

A political party seeks to win elections and directly hold government power, standing candidates under its own name. A pressure group seeks to influence government policy on specific issues (like labour rights, environmental protection, or business interests) without contesting elections or seeking to govern itself.

Example 1: An organization campaigns for stronger environmental protection laws by lobbying lawmakers and organizing public awareness campaigns, but does not put forward candidates for election. Is this a political party or a pressure group?
This is a pressure group -- it seeks to influence government policy on a specific issue (environmental protection) through lobbying and advocacy, but does not attempt to win elections or hold government power directly, which is what would define it as a political party instead.

## Party systems

A one-party system legally permits only a single party to hold power, common in some authoritarian states. A two-party system has two major parties that realistically compete for power (though smaller parties may exist), as traditionally seen in the USA. A multi-party system has several parties genuinely competing, often leading to coalition governments where no single party wins an outright majority -- common across much of Africa and Europe, including Nigeria.""",
        "related_topics": ["Electoral Systems", "Nigerian Government/Politics"],
    },
    {
        "subject": "Government",
        "topic": "Local Government",
        "title": "Local Government",
        "summary": "The functions and structure of local government, and why it matters for grassroots development.",
        "glossary": [
            {"term": "Local government", "definition": "the level of government closest to citizens, responsible for local services and administration"},
            {"term": "Grassroots development", "definition": "development efforts focused directly on communities at the local level"},
            {"term": "Devolution", "definition": "the transfer of specific powers from a central government to lower levels of government"},
        ],
        "content_md": r"""## Functions of local government

Local government is typically responsible for services closest to citizens' daily lives: primary healthcare, primary education, local roads, markets, sanitation, and birth/death registration. Being closer to the people than state or federal government, it is meant to respond more directly to local needs and priorities.

## Structure of local government in Nigeria

Nigeria's 774 Local Government Areas (LGAs) form the third tier of government, below federal and state government. Each LGA is typically administered by an elected chairman and a legislative council (councillors), though in practice many LGAs have at times been run by unelected caretaker committees, which is a recurring point of debate about local government autonomy in Nigeria.

Example 1: Explain why local government is often described as the level of government "closest to the people."
Local government handles day-to-day services and issues that directly affect ordinary citizens' daily lives -- like local roads, markets, and primary healthcare -- and its officials are (in principle) more physically accessible and directly accountable to the specific communities they serve, compared to state or federal officials managing much larger populations and areas.

## Why local government matters

Effective local government is central to grassroots development -- addressing needs at the community level often more efficiently than a distant central government could, and giving citizens a more direct channel to participate in decisions that affect them. Weak or poorly funded local government, by contrast, can leave basic community-level needs unmet even when higher levels of government are functioning.""",
        "related_topics": ["Nigerian Government/Politics", "Systems of Government"],
    },
    {
        "subject": "Government",
        "topic": "Comparative Government",
        "title": "Comparative Government",
        "summary": "Why political scientists compare different countries' government systems, and the difference between bicameral and unicameral legislatures.",
        "glossary": [
            {"term": "Comparative government", "definition": "the study of comparing different countries' political systems, institutions, and processes"},
            {"term": "Bicameral legislature", "definition": "a legislature with two chambers/houses, e.g. Nigeria's Senate and House of Representatives"},
            {"term": "Unicameral legislature", "definition": "a legislature with a single chamber/house"},
        ],
        "content_md": r"""## Why compare government systems

Comparing how different countries organize their governments helps identify what works well (or poorly) under different circumstances, and why. It highlights that there's no single "correct" way to organize government -- choices like federal vs unitary, presidential vs parliamentary, and bicameral vs unicameral all involve trade-offs suited to a country's specific history, size, and diversity.

## Comparing presidential systems: the USA and Nigeria

Both the USA and Nigeria use presidential systems with a directly elected president serving as both head of state and head of government, separate from the legislature, and a federal structure dividing power between central and state governments. A key difference is the exact balance of power and the specific mechanisms for legislative-executive checks, shaped by each country's own constitutional history.

Example 1: Explain one similarity between Nigeria's and the USA's systems of government.
Both are federal, presidential systems -- power is constitutionally divided between a central government and states, and in both countries the president is directly elected, serving a fixed term separate from the legislature, unlike a parliamentary system where the executive is drawn from and dependent on the legislature.

## Bicameral vs unicameral legislatures

A bicameral legislature has two chambers (like Nigeria's Senate and House of Representatives, or the UK's House of Commons and House of Lords), often allowing more thorough scrutiny of laws as they pass through two separate bodies. A unicameral legislature has only one chamber, which can make law-making faster and simpler, common in smaller or more centralized states.""",
        "related_topics": ["Systems of Government", "International Relations"],
    },
    {
        "subject": "Commerce",
        "topic": "Commerce Fundamentals and Occupations",
        "title": "Commerce Fundamentals and Occupations",
        "summary": "What commerce covers beyond simple buying and selling, and how occupations are classified.",
        "glossary": [
            {"term": "Commerce", "definition": "all activities involved in the exchange of goods and services, including trade and the services (aids to trade) that support it"},
            {"term": "Trade", "definition": "the direct buying and selling of goods and services"},
            {"term": "Aids to trade", "definition": "the supporting services that make trade possible, e.g. banking, insurance, transport, warehousing, advertising"},
            {"term": "Direct service occupation", "definition": "an occupation providing a service directly to the public, e.g. teaching, medicine"},
        ],
        "content_md": r"""## What commerce covers

Commerce is broader than just trade (buying and selling). It also includes the "aids to trade" -- services that make trade possible and efficient: banking (finance), insurance (risk protection), transport (moving goods), warehousing (storage), advertising (informing buyers), and communication (coordinating business activity).

Example 1: A trader needs to store unsold goods safely, insure them against fire damage, and transport them to a distant market. Name the three aids to trade involved.
Warehousing (storing the goods), insurance (protecting against fire damage risk), and transport (moving the goods to market) -- each is a distinct aid to trade supporting the underlying buying-and-selling activity.

## Classifying occupations

Occupations are broadly classified as direct services (providing a service straight to the public, like teaching, medicine, or hairdressing) or commerce/trade-related occupations (buying, selling, and the aids to trade, like a shopkeeper, banker, or insurance agent). This distinction helps explain how different parts of an economy contribute to getting goods and services from producers to the people who need them.""",
        "related_topics": ["Business Organisation and Management", "International, Wholesale, and Retail Trade"],
    },
    {
        "subject": "Commerce",
        "topic": "Business Organisation and Management",
        "title": "Business Organisation and Management",
        "summary": "The main forms of business ownership used in commerce, and the core functions of management.",
        "glossary": [
            {"term": "Sole trader", "definition": "a business owned and run by one person"},
            {"term": "Cooperative society", "definition": "a business owned and democratically run by its members, who share in its benefits"},
            {"term": "Management", "definition": "the process of planning, organizing, directing, and controlling resources to achieve business goals"},
        ],
        "content_md": r"""## Forms of business ownership

A sole trader owns and runs the business alone, keeping full control and profit but bearing unlimited liability. A partnership is owned by two or more people sharing capital, management, and liability. A cooperative society is owned and democratically controlled by its members (often producers or consumers), who pool resources for shared benefit, with profits typically distributed based on members' participation rather than shares owned. A limited liability company is owned by shareholders, whose liability is limited to their investment.

Example 1: Explain one key difference between a cooperative society and a limited liability company.
A cooperative society is run democratically -- typically one member, one vote, regardless of how much each member has contributed -- and profits are usually shared based on participation (e.g. purchases made or produce supplied). A limited liability company gives voting power and profit share in proportion to shares owned, so larger shareholders have proportionally more influence and reward.

## Functions of management

Management involves four core functions: planning (setting goals and deciding how to achieve them), organizing (arranging resources and people to carry out the plan), directing (leading and motivating staff to perform), and controlling (monitoring performance against goals and correcting deviations).""",
        "related_topics": ["Commerce Fundamentals and Occupations", "Law of Contract and Agency"],
    },
    {
        "subject": "Commerce",
        "topic": "Money, Banking, and Stock Exchange",
        "title": "Money, Banking, and Stock Exchange",
        "summary": "Banking services businesses rely on, and how the stock exchange lets companies raise capital through shares.",
        "glossary": [
            {"term": "Cheque", "definition": "a written order instructing a bank to pay a stated sum from the account holder's account"},
            {"term": "Stock exchange", "definition": "an organized market where shares and other securities are bought and sold"},
            {"term": "Share", "definition": "a unit of ownership in a company, entitling the holder to a portion of its profits and, usually, voting rights"},
            {"term": "Debenture", "definition": "a loan to a company that pays fixed interest, but does not give ownership or voting rights"},
        ],
        "content_md": r"""## Banking services for businesses

Commercial banks offer current accounts (for frequent transactions, often with chequebook and overdraft facilities, usually no/low interest) and savings accounts (for accumulating funds, earning interest, with more limited transaction frequency). Cheques let account holders make payments without handling physical cash, by instructing the bank to transfer a stated sum to the payee.

## The stock exchange

A stock exchange is an organized marketplace where shares of publicly listed companies (and other securities like government bonds) are bought and sold. Companies raise capital by issuing shares to investors; in return, shareholders own a portion of the company and typically get voting rights and a share of profits (dividends).

Example 1: Explain the difference between a share and a debenture as ways for a company to raise capital.
A share represents part-ownership of the company -- the shareholder gets voting rights and a variable dividend depending on profits, and shares the business's risk. A debenture is essentially a loan to the company -- the debenture holder is a creditor, not an owner, and receives a fixed interest payment regardless of the company's profit level, with no voting rights, but is typically repaid before shareholders receive anything if the company is wound up.""",
        "related_topics": ["Business Organisation and Management", "Production and Insurance"],
    },
    {
        "subject": "Commerce",
        "topic": "Consumer Protection, Warehousing, and Taxation",
        "title": "Consumer Protection, Warehousing, and Taxation",
        "summary": "Consumers' rights and how they're protected, the role and types of warehousing, and how taxation affects trade.",
        "glossary": [
            {"term": "Consumer protection", "definition": "laws and measures designed to safeguard buyers from unfair or unsafe trading practices"},
            {"term": "Warehousing", "definition": "the storage of goods between production and eventual sale or use"},
            {"term": "Bonded warehouse", "definition": "a warehouse where imported goods can be stored without immediately paying import duty, until they're released for sale"},
        ],
        "content_md": r"""## Consumer protection

Consumer protection covers rights like receiving goods that are safe, of satisfactory quality, and as described, along with protection against false advertising and unfair contract terms. Government agencies and consumer protection laws exist to enforce these rights, giving buyers recourse (like refunds, replacements, or compensation) when a seller fails to meet them.

## Warehousing

Warehousing bridges the time gap between production and sale/use, allowing goods to be stored safely until needed. Private warehouses are owned by a single business for its own goods; public warehouses store goods for multiple different owners for a fee; bonded warehouses store imported goods under customs supervision, deferring import duty payment until the goods are actually released for sale.

Example 1: Explain the advantage of a bonded warehouse for an importer who isn't yet ready to sell their goods.
A bonded warehouse lets the importer store the goods without paying import duty immediately -- duty is only paid when the goods are released from the warehouse for sale. This helps the importer's cash flow, since they aren't forced to pay duty on goods sitting unsold in storage.

## Taxation and trade

Governments often levy indirect taxes on goods -- like import duties (on goods brought into the country) and excise duties (on certain goods produced domestically, like alcohol or tobacco) -- which affect prices and trading decisions, and are an important source of government revenue.""",
        "related_topics": ["International, Wholesale, and Retail Trade", "Production and Insurance"],
    },
    {
        "subject": "Commerce",
        "topic": "Office Practice and ICT",
        "title": "Office Practice and ICT",
        "summary": "The core functions of a business office, common office equipment, and the growing role of ICT and e-commerce.",
        "glossary": [
            {"term": "Filing", "definition": "the systematic storage and organization of documents for easy retrieval"},
            {"term": "ICT", "definition": "Information and Communication Technology -- tools and systems used to process, store, and communicate information"},
            {"term": "E-commerce", "definition": "buying and selling goods or services over the internet"},
        ],
        "content_md": r"""## Functions of an office

An office coordinates a business's administrative activities: receiving and sending correspondence, keeping records, processing information, and supporting communication between departments and with outside parties (customers, suppliers, government agencies).

## Filing and office equipment

Good filing systems (alphabetical, numerical, or subject-based) let a business retrieve important documents quickly when needed, rather than searching through disorganized paperwork. Common office equipment includes computers, printers, telephones, and photocopiers -- each supporting different parts of the office's information-processing role.

## ICT and e-commerce

Modern offices rely heavily on ICT -- computers, the internet, and specialized software -- to process transactions, communicate, and store records far more efficiently than manual paper-based methods. E-commerce (buying and selling over the internet) has grown alongside this, letting businesses reach customers without a physical shop, though it still relies on the traditional aids to trade like transport (to deliver goods) and banking (to process payments).

Example 1: Explain one advantage e-commerce offers a small business compared to relying only on a physical shop.
E-commerce lets a small business reach customers far beyond its immediate physical location, potentially nationally or internationally, without the high cost of opening physical shops in each new area -- significantly widening its potential market at a much lower cost.""",
        "related_topics": ["Communication and Transportation", "Commerce Fundamentals and Occupations"],
    },
    {
        "subject": "Commerce",
        "topic": "Production and Insurance",
        "title": "Production and Insurance",
        "summary": "The different stages/types of production, and the core principles that make insurance work.",
        "glossary": [
            {"term": "Extractive production", "definition": "production that obtains raw materials directly from nature, e.g. mining, fishing"},
            {"term": "Insurance", "definition": "a system where policyholders pay a premium to be compensated for specified future losses"},
            {"term": "Premium", "definition": "the amount a policyholder pays, usually regularly, for insurance cover"},
            {"term": "Insurable interest", "definition": "a financial stake that would cause a person genuine loss if the insured item were damaged or lost"},
        ],
        "content_md": r"""## Stages and types of production

Production is often classified into stages: extractive (obtaining raw materials directly from nature, like mining or farming), manufacturing/construction (converting raw materials into finished or semi-finished goods), and services (production of intangible things like banking or transport, rather than physical goods).

## Principles of insurance

Insurance works by pooling risk: many people pay a relatively small, regular premium, and the pooled fund compensates the few who actually suffer the insured loss. For a valid insurance contract, key principles apply: insurable interest (the policyholder must genuinely stand to lose financially if the insured event happens -- you can't insure a stranger's house), utmost good faith (both parties must honestly disclose all relevant facts), and indemnity (compensation restores the policyholder to their financial position before the loss, not more).

Example 1: Explain why a person cannot take out a fire insurance policy on a neighbour's house that they have no financial stake in.
This would fail the principle of insurable interest -- insurance requires the policyholder to have a genuine financial stake that would cause them real loss if the insured event occurred. Without owning or having a financial interest in the neighbour's house, there's no genuine loss to insure against, and allowing such policies would create a dangerous incentive for the policyholder to cause the loss deliberately.""",
        "related_topics": ["Money, Banking, and Stock Exchange", "Consumer Protection, Warehousing, and Taxation"],
    },
    {
        "subject": "Commerce",
        "topic": "Law of Contract and Agency",
        "title": "Law of Contract and Agency",
        "summary": "What makes a contract legally valid, and how an agent's relationship with their principal works.",
        "glossary": [
            {"term": "Contract", "definition": "a legally binding agreement between two or more parties"},
            {"term": "Offer", "definition": "a clear proposal by one party, showing willingness to enter a contract on specific terms"},
            {"term": "Acceptance", "definition": "an unqualified agreement to the exact terms of an offer, creating a binding contract"},
            {"term": "Agent", "definition": "a person authorized to act on behalf of another (the principal) in dealings with third parties"},
        ],
        "content_md": r"""## Elements of a valid contract

A legally valid contract needs: an offer (a clear proposal), acceptance (unqualified agreement to that exact offer), consideration (something of value exchanged by each party), capacity (both parties must be legally able to contract, e.g. of sound mind and legal age), and legality (the contract's purpose must not be illegal).

Example 1: A trader offers to sell 50 bags of rice at a stated price, and the buyer agrees to the exact terms and pays a deposit. Identify the offer, acceptance, and consideration in this scenario.
The offer is the trader's proposal to sell the rice at the stated price. The acceptance is the buyer agreeing to those exact terms. The consideration is the deposit paid by the buyer (and the promise of the rice from the trader) -- each party is giving something of value in exchange for what the other offers.

## Agency

An agent is authorized to act on behalf of another person or business (the principal) in dealings with third parties -- for example, negotiating deals, signing contracts, or making purchases on the principal's behalf. Common types include a general agent (authorized to act across a range of matters) and a special agent (authorized for one specific task or transaction only). The agent owes the principal duties of good faith, obedience to lawful instructions, and reasonable care in carrying out the agency.""",
        "related_topics": ["Business Organisation and Management", "Marketing and Advertising"],
    },
    {
        "subject": "Commerce",
        "topic": "Marketing and Advertising",
        "title": "Marketing and Advertising",
        "summary": "The four elements of the marketing mix, and the role advertising plays in reaching customers.",
        "glossary": [
            {"term": "Marketing", "definition": "the process of identifying, anticipating, and satisfying customer needs profitably"},
            {"term": "Marketing mix", "definition": "the combination of product, price, place, and promotion decisions a business makes to market a good"},
            {"term": "Advertising", "definition": "paid, non-personal communication designed to inform or persuade an audience about a product or service"},
            {"term": "Branding", "definition": "creating a distinct identity and image for a product or business to distinguish it from competitors"},
        ],
        "content_md": r"""## The marketing mix

The marketing mix ("the four Ps") describes the key decisions a business makes to market its product: Product (what's being offered, its features and quality), Price (how much it costs, and the pricing strategy used), Place (how and where the product reaches customers, i.e. distribution), and Promotion (how the business communicates with and persuades customers, including advertising).

Example 1: A company launches a premium smartphone, sells it only through select high-end stores, and prices it well above competitors, alongside a glossy advertising campaign emphasizing exclusivity. Identify which element of the marketing mix "selling only through select high-end stores" represents.
This represents Place -- the decision about where and how the product is distributed to reach customers, in this case deliberately limiting distribution to reinforce the product's premium, exclusive positioning.

## Advertising

Advertising is paid, non-personal promotion aimed at informing potential customers about a product and persuading them to buy it. It can use various media -- television, radio, print, billboards, social media/online -- chosen based on the target audience and budget. Effective advertising, alongside consistent branding (a distinct name, logo, and image), helps a product stand out and build customer loyalty over time.""",
        "related_topics": ["Law of Contract and Agency", "International, Wholesale, and Retail Trade"],
    },
    {
        "subject": "Commerce",
        "topic": "Communication and Transportation",
        "title": "Communication and Transportation",
        "summary": "How businesses communicate internally and externally, and the different modes of transport used to move goods.",
        "glossary": [
            {"term": "Communication", "definition": "the process of exchanging information between people or organizations"},
            {"term": "Mode of transport", "definition": "a specific method of moving goods or people, e.g. road, rail, water, air, or pipeline"},
            {"term": "Bill of lading", "definition": "a document issued by a shipping carrier, acting as a receipt for goods and evidence of the shipping contract"},
        ],
        "content_md": r"""## Communication in business

Businesses communicate through many channels: face-to-face meetings, telephone, letters, email, and increasingly instant digital messaging. Effective communication -- both within a business (between staff/departments) and externally (with customers and suppliers) -- is essential for coordinating activities and building trust with trading partners.

## Modes of transport

Road transport is flexible and reaches almost anywhere, well-suited to shorter distances and door-to-door delivery, but can be slower over very long distances and affected by traffic/road conditions. Rail transport efficiently moves large, heavy loads over long land distances but is limited to fixed routes. Water transport (ships) is the cheapest way to move very large quantities over long distances (especially internationally) but is slow. Air transport is the fastest option, suited to urgent or high-value/perishable goods, but is the most expensive. Pipeline transport moves liquids and gases (like crude oil) continuously and efficiently over fixed routes.

Example 1: A company needs to export a large quantity of crude oil to another continent as cheaply as possible, with no urgency about delivery time. Which mode of transport is most suitable, and why?
Water transport (ship) is most suitable -- it's the cheapest option for moving very large quantities over long international distances, and since there's no time urgency, its relatively slow speed compared to air transport isn't a drawback here.

## Transport documents

Transport of goods, especially internationally, is documented for legal and tracking purposes -- a bill of lading (for sea transport) or waybill (for road/air/rail) serves as a receipt confirming the carrier has received the goods, evidence of the contract of carriage, and often a document needed to claim the goods at their destination.""",
        "related_topics": ["Office Practice and ICT", "International, Wholesale, and Retail Trade"],
    },
    {
        "subject": "Commerce",
        "topic": "International, Wholesale, and Retail Trade",
        "title": "International, Wholesale, and Retail Trade",
        "summary": "The chain of distribution from producer to consumer, and the basics of import, export, and entrepot trade.",
        "glossary": [
            {"term": "Wholesaler", "definition": "a business that buys goods in bulk from producers and sells smaller quantities on to retailers"},
            {"term": "Retailer", "definition": "a business that sells goods directly to the final consumer, usually in small quantities"},
            {"term": "Import", "definition": "bringing goods into a country from abroad"},
            {"term": "Export", "definition": "sending goods out of a country to be sold abroad"},
            {"term": "Entrepot trade", "definition": "importing goods into a country not to sell there, but to re-export them (often after minor processing) to another country"},
        ],
        "content_md": r"""## The chain of distribution

Goods typically move from producer to wholesaler (who buys in bulk and breaks it into smaller quantities), to retailer (who sells small quantities directly to the public), to the final consumer. This chain exists because producers usually can't efficiently sell tiny quantities directly to millions of individual consumers, and wholesalers/retailers each add value by bridging that gap in scale and location.

Example 1: Explain one function a wholesaler performs that benefits both producers and retailers.
A wholesaler buys in bulk from producers (saving producers the cost and effort of dealing with many small individual retail orders) and breaks that bulk down into smaller quantities that retailers can afford and manage to stock -- bridging the gap between large-scale production and small-scale retail demand, benefiting both sides of the chain.

## International trade in commerce

Importing brings foreign goods into a country (often things not efficiently produced domestically); exporting sends domestically produced goods abroad for sale, earning foreign exchange. Entrepot trade involves importing goods specifically to re-export them to a third country, often taking advantage of a country's strategic trading location, port facilities, or processing capabilities, rather than for domestic consumption.""",
        "related_topics": ["Commerce Fundamentals and Occupations", "Consumer Protection, Warehousing, and Taxation"],
    },
    {
        "subject": "Accounting",
        "topic": "Accounting Fundamentals",
        "title": "Accounting Fundamentals",
        "summary": "The accounting equation, the double-entry principle behind every transaction, and the main branches of accounting.",
        "glossary": [
            {"term": "Asset", "definition": "something a business owns that has value, e.g. cash, equipment, inventory"},
            {"term": "Liability", "definition": "something a business owes to others, e.g. loans, unpaid bills"},
            {"term": "Capital", "definition": "the owner's investment/stake in the business, also called owner's equity"},
            {"term": "Double entry", "definition": "the principle that every transaction affects at least two accounts -- a debit in one, a credit in another -- keeping the accounting equation balanced"},
        ],
        "content_md": r"""## The accounting equation

Every business's financial position obeys one core equation: \(Assets = Liabilities + Capital\). This must always balance, since everything a business owns (assets) was funded either by borrowing (liabilities) or by the owner's own investment (capital).

Example 1: A business has assets of ₦500,000 and liabilities of ₦120,000. Find the owner's capital.
Rearranging the equation: \(Capital = Assets - Liabilities = 500{,}000 - 120{,}000 = 380{,}000\).

## The double-entry principle

Every transaction has two sides and affects at least two accounts: a debit entry in one account and an equal credit entry in another. This keeps the accounting equation balanced after every single transaction, and is the foundation of all bookkeeping.

Example 2: A business buys equipment for ₦50,000 cash. Identify the two accounts affected and which side (debit/credit) each is recorded on.
The equipment account is debited ₦50,000 (an asset increases). The cash account is credited ₦50,000 (another asset decreases, since cash was paid out) -- two accounts affected, keeping the equation balanced.

## Branches of accounting

Financial accounting records and reports a business's transactions and financial position, mainly for external users (investors, tax authorities, creditors). Cost accounting focuses on tracking and controlling the costs of producing goods or services. Management accounting provides information to help internal management make decisions, focusing on planning and control rather than external reporting requirements.""",
        "related_topics": ["Ledger, Journal, and Source Documents", "Final Accounts and Trial Balance"],
    },
    {
        "subject": "Accounting",
        "topic": "Ledger, Journal, and Source Documents",
        "title": "Ledger, Journal, and Source Documents",
        "summary": "The documents that trigger accounting entries, and how transactions move from the journal into the ledger.",
        "glossary": [
            {"term": "Source document", "definition": "the original paper or record evidencing a transaction, e.g. an invoice or receipt"},
            {"term": "Journal", "definition": "the book of original entry, where transactions are first recorded in date order before posting to the ledger"},
            {"term": "Ledger", "definition": "the set of accounts where transactions are grouped and posted, organized by account rather than by date"},
            {"term": "Invoice", "definition": "a document issued by a seller to a buyer, detailing goods/services supplied and the amount owed"},
        ],
        "content_md": r"""## Source documents

Every accounting entry starts from a source document, providing evidence of a transaction: an invoice (details of a credit sale/purchase), a receipt (proof of a cash payment received), a credit note (reduces an amount owed, e.g. for returned goods), and a debit note (increases an amount owed, e.g. for an undercharge).

## The journal

The journal is the book of original/prime entry, where every transaction is first recorded, in date order, showing which accounts to debit and credit, with a brief narration explaining the transaction.

Example 1: Record the journal entry for a business buying office furniture worth ₦80,000 in cash.
Debit: Furniture account, ₦80,000. Credit: Cash account, ₦80,000. Narration: Being purchase of office furniture for cash.

## The ledger

After being recorded in the journal, each transaction is "posted" (transferred) into the ledger -- a collection of individual accounts (like the furniture account, cash account, etc.), each usually shown as a "T-account" with debit entries on the left and credit entries on the right. This grouping by account (rather than by date, as in the journal) makes it easy to see the running balance and full history of any one account.

Example 2: Using the furniture purchase from Example 1, describe how it would appear in the two ledger T-accounts affected.
In the Furniture account, ₦80,000 is entered on the debit (left) side. In the Cash account, ₦80,000 is entered on the credit (right) side -- mirroring the journal entry, now organized within each account's own running record.""",
        "related_topics": ["Accounting Fundamentals", "Cash Book and Bank Reconciliation"],
    },
    {
        "subject": "Accounting",
        "topic": "Stock Valuation and Depreciation",
        "title": "Stock Valuation and Depreciation",
        "summary": "The main methods for valuing closing stock, and the two most common ways to calculate depreciation on fixed assets.",
        "glossary": [
            {"term": "FIFO (First In, First Out)", "definition": "a stock valuation method assuming the oldest stock (bought first) is sold first"},
            {"term": "Depreciation", "definition": "the systematic allocation of a fixed asset's cost as an expense over its useful life"},
            {"term": "Straight-line method", "definition": "a depreciation method charging an equal amount of depreciation each year"},
            {"term": "Reducing balance method", "definition": "a depreciation method charging a fixed percentage of the asset's remaining (book) value each year"},
        ],
        "content_md": r"""## Stock valuation

FIFO (First In, First Out) assumes the oldest stock is sold first, so closing stock is valued at the most recent purchase prices. This matters because purchase prices change over time, and the valuation method chosen affects the reported cost of goods sold and closing stock value.

Example 1: A business bought 100 units at ₦50 each, then later bought 100 more units at ₦60 each (200 units total). It sold 120 units. Using FIFO, find the value of the closing stock.
Closing stock = \(200 - 120 = 80\) units. Under FIFO, the units sold are assumed to come from the oldest stock first: all 100 units at ₦50 are used up, then 20 units from the ₦60 batch. That leaves \(100 - 20 = 80\) units of the ₦60 batch remaining, so the closing stock is valued at \(80 \times 60 = 4{,}800\) naira.

## Depreciation

Depreciation spreads a fixed asset's cost as an expense across the years it's used, matching the expense to the periods that benefit from the asset. The straight-line method charges an equal amount each year: \(\text{annual depreciation} = \dfrac{\text{cost} - \text{residual value}}{\text{useful life}}\). The reducing balance method charges a fixed percentage of the asset's remaining book value each year, so the depreciation charge is largest in the early years and shrinks over time.

Example 2: A machine costs ₦200,000, has an estimated residual value of ₦20,000, and a useful life of 6 years. Find the annual depreciation using the straight-line method.
\(\text{Annual depreciation} = \dfrac{200{,}000 - 20{,}000}{6} = \dfrac{180{,}000}{6} = 30{,}000\) per year.""",
        "related_topics": ["Final Accounts and Trial Balance", "Manufacturing and Departmental Accounts"],
    },
    {
        "subject": "Accounting",
        "topic": "Company and Partnership Accounts",
        "title": "Company and Partnership Accounts",
        "summary": "How partnership profits are shared between partners, and the basics of company share capital and dividends.",
        "glossary": [
            {"term": "Partnership deed", "definition": "a written agreement setting out the terms partners have agreed to run their business by, including profit-sharing"},
            {"term": "Profit-sharing ratio", "definition": "the agreed proportion in which partners divide the business's profits (and losses)"},
            {"term": "Share capital", "definition": "the total amount raised by a company through issuing shares to shareholders"},
            {"term": "Dividend", "definition": "a portion of a company's profit distributed to its shareholders"},
        ],
        "content_md": r"""## Partnership accounts

Partners share profits and losses according to their agreed profit-sharing ratio, usually set out in a partnership deed. Each partner typically has a capital account (their fixed long-term investment) and a current account (tracking their share of profits, drawings, and interest).

Example 1: Two partners, A and B, agree to share profits in a 3:2 ratio. If the partnership's profit for the year is ₦100,000, find each partner's share.
Total ratio parts = 3 + 2 = 5. A's share = \(\dfrac{3}{5} \times 100{,}000 = 60{,}000\). B's share = \(\dfrac{2}{5} \times 100{,}000 = 40{,}000\).

## Company accounts

A limited liability company raises capital by issuing shares to shareholders, who become part-owners. The total amount raised this way is the company's share capital. After covering expenses and tax, remaining profit can be distributed to shareholders as dividends (usually per share held), or retained within the business for reinvestment (retained earnings).

Example 2: A company declares a dividend of ₦2 per share. A shareholder owns 5,000 shares. Find the total dividend they receive.
Total dividend = \(2 \times 5{,}000 = 10{,}000\) naira.""",
        "related_topics": ["Accounting Fundamentals", "Final Accounts and Trial Balance"],
    },
    {
        "subject": "Accounting",
        "topic": "Public Sector and Not-for-Profit Accounts",
        "title": "Public Sector and Not-for-Profit Accounts",
        "summary": "How not-for-profit organizations track cash movements and overall financial performance differently from profit-making businesses.",
        "glossary": [
            {"term": "Receipts and payments account", "definition": "a summary of all cash received and paid by a not-for-profit organization during a period"},
            {"term": "Income and expenditure account", "definition": "a not-for-profit organization's equivalent of a profit and loss account, showing surplus or deficit"},
            {"term": "Subscription", "definition": "regular membership fees paid by members of a club or society"},
        ],
        "content_md": r"""## Receipts and payments account vs income and expenditure account

A receipts and payments account is a simple summary of all cash actually received and paid during a period -- like a cash book summary, not adjusted for amounts owed or prepaid. An income and expenditure account is the not-for-profit equivalent of a profit and loss account -- it applies accrual accounting, adjusting for amounts owed or paid in advance, to show the true surplus or deficit for the period, not just cash movements.

Example 1: A club's receipts and payments account shows subscriptions received of ₦300,000 during the year, but ₦20,000 of last year's subscriptions were received this year, and ₦15,000 of this year's subscriptions are still outstanding. Find the subscription income for the income and expenditure account.
Subscription income = cash received - amounts relating to a previous period + amounts owed for this period = \(300{,}000 - 20{,}000 + 15{,}000 = 295{,}000\).

## Fund accounting for not-for-profits

Instead of "capital" as used by profit-making businesses, not-for-profit organizations often refer to their net worth as "accumulated fund" -- built up from surpluses over time (a surplus adds to it, a deficit reduces it), since there's no owner drawing profit and no share capital in the traditional sense.""",
        "related_topics": ["Final Accounts and Trial Balance", "Cash Book and Bank Reconciliation"],
    },
    {
        "subject": "Accounting",
        "topic": "Manufacturing and Departmental Accounts",
        "title": "Manufacturing and Departmental Accounts",
        "summary": "How manufacturing accounts calculate the cost of goods produced, and how departmental accounts split shared costs.",
        "glossary": [
            {"term": "Manufacturing account", "definition": "an account calculating the total cost of goods manufactured during a period"},
            {"term": "Prime cost", "definition": "the total of direct materials, direct labour, and direct expenses used in production"},
            {"term": "Factory overhead", "definition": "indirect production costs that can't be traced directly to a specific unit, e.g. factory rent, supervisor salaries"},
            {"term": "Departmental account", "definition": "an account showing the profit or loss of one specific department within a larger business"},
        ],
        "content_md": r"""## The manufacturing account

A manufacturing account calculates the total cost of goods produced in a period. It starts with direct materials used, adds direct labour and direct expenses to get the prime cost, then adds factory overheads (indirect costs like factory rent and supervision) to reach the total cost of production.

Example 1: A business uses direct materials of ₦300,000, direct labour of ₦150,000, and direct expenses of ₦20,000. Find the prime cost.
\(\text{Prime cost} = \text{direct materials} + \text{direct labour} + \text{direct expenses} = 300{,}000 + 150{,}000 + 20{,}000 = 470{,}000\).

## Departmental accounts

A business with multiple departments (e.g. a store with separate clothing and electronics departments) may prepare departmental accounts to see each department's individual profitability, not just the business's overall result. Costs that relate specifically to one department (like that department's staff wages) are charged directly to it; shared costs (like rent for the whole building) are apportioned between departments using a fair basis, such as floor space occupied.

Example 2: A shared electricity bill of ₦60,000 is apportioned between two departments based on floor space: Department A occupies 40% of the floor space, Department B occupies 60%. Find each department's share of the electricity cost.
Department A: \(0.40 \times 60{,}000 = 24{,}000\). Department B: \(0.60 \times 60{,}000 = 36{,}000\).""",
        "related_topics": ["Stock Valuation and Depreciation", "Final Accounts and Trial Balance"],
    },
    {
        "subject": "Accounting",
        "topic": "Cash Book and Bank Reconciliation",
        "title": "Cash Book and Bank Reconciliation",
        "summary": "How a cash book records cash and bank transactions, and how to reconcile it with the bank statement.",
        "glossary": [
            {"term": "Cash book", "definition": "a book recording all cash and bank receipts and payments, acting as both a book of original entry and a ledger account"},
            {"term": "Bank reconciliation statement", "definition": "a statement explaining the differences between the cash book's bank balance and the bank statement balance"},
            {"term": "Unpresented cheque", "definition": "a cheque written and recorded in the cash book, but not yet cashed/cleared by the bank"},
            {"term": "Uncredited cheque", "definition": "a cheque received and recorded in the cash book, but not yet cleared into the bank account"},
        ],
        "content_md": r"""## The cash book

A cash book records all cash and bank transactions in date order, often as a "two-column" cash book (one column for cash, one for bank) or "three-column" (adding a discount column). Unlike most ledger accounts, the cash book serves double duty -- it's both a book of original entry and the actual cash/bank ledger account.

## Bank reconciliation

A business's cash book balance for its bank account often differs from the balance shown on the bank statement, due to timing differences -- most commonly unpresented cheques (written and deducted in the cash book, but not yet cashed by the recipient) and uncredited cheques/deposits (received and added in the cash book, but not yet cleared by the bank). A bank reconciliation statement explains these differences to confirm both records are otherwise correct.

Example 1: A cash book shows a bank balance of ₦150,000. The bank statement shows ₦180,000. There is an unpresented cheque of ₦40,000 and an uncredited deposit of ₦10,000. Reconcile the two balances.
Starting from the bank statement balance: \(180{,}000 - 40{,}000 \text{ (unpresented cheque)} + 10{,}000 \text{ (uncredited deposit)} = 150{,}000\) -- matching the cash book balance, confirming the reconciliation is correct.""",
        "related_topics": ["Ledger, Journal, and Source Documents", "Public Sector and Not-for-Profit Accounts"],
    },
    {
        "subject": "Accounting",
        "topic": "Office Practice, ICT, and Banking",
        "title": "Office Practice, ICT, and Banking",
        "summary": "How ICT has changed accounting record-keeping, and the banking services most relevant to a business's accounting function.",
        "glossary": [
            {"term": "Computerized accounting", "definition": "using accounting software to record, process, and report financial transactions instead of manual books"},
            {"term": "E-banking", "definition": "conducting banking transactions electronically, e.g. online transfers, mobile banking"},
        ],
        "content_md": r"""## The role of ICT in accounting

Computerized accounting systems automate much of the manual bookkeeping process -- automatically posting entries to the correct ledger accounts, calculating balances, and generating reports (like trial balances and final accounts) instantly, with far less risk of arithmetic error than fully manual methods. This has made routine accounting tasks faster and freed accountants to focus more on analysis and decision-support.

Example 1: State one advantage of computerized accounting over manual bookkeeping.
Computerized accounting drastically reduces arithmetic errors (calculations are done automatically) and speeds up producing reports like trial balances, since figures update instantly as transactions are entered, rather than requiring manual recalculation each time.

## Banking services relevant to accounting

E-banking (online transfers, mobile banking, electronic payments) has streamlined how businesses make and receive payments, and how those transactions are recorded in accounting systems -- often integrating directly with accounting software, reducing the manual work needed to match bank statements against accounting records (making bank reconciliation faster too).""",
        "related_topics": ["Cash Book and Bank Reconciliation", "Ledger, Journal, and Source Documents"],
    },
    {
        "subject": "Accounting",
        "topic": "Final Accounts and Trial Balance",
        "title": "Final Accounts and Trial Balance",
        "summary": "How a trial balance checks the ledger, and how the trading, profit and loss account, and balance sheet are built from it.",
        "glossary": [
            {"term": "Trial balance", "definition": "a list of all ledger account balances, checking that total debits equal total credits"},
            {"term": "Trading account", "definition": "an account calculating gross profit, from sales revenue and cost of goods sold"},
            {"term": "Gross profit", "definition": "sales revenue minus the cost of goods sold"},
            {"term": "Net profit", "definition": "gross profit minus all other business expenses"},
            {"term": "Balance sheet", "definition": "a statement showing a business's assets, liabilities, and capital at a specific point in time"},
        ],
        "content_md": r"""## The trial balance

A trial balance lists every ledger account's balance, split into debit and credit columns, to check that total debits equal total credits -- a basic (though not foolproof) check that the double-entry bookkeeping has been applied consistently. If the two totals don't match, an error exists somewhere and must be found before final accounts can be prepared.

Example 1: A trial balance shows total debits of ₦850,000 and total credits of ₦830,000. What does this tell you?
The totals don't match, meaning there's an error somewhere in the ledger -- a transaction recorded incorrectly, an account omitted, or a one-sided entry. The ₦20,000 difference must be investigated and corrected before reliable final accounts can be prepared.

## The trading and profit and loss account

The trading account calculates gross profit: \(\text{gross profit} = \text{sales revenue} - \text{cost of goods sold}\). The profit and loss account then deducts all other business expenses (rent, salaries, utilities, depreciation, etc.) from gross profit to find net profit.

Example 2: A business has sales revenue of ₦500,000, cost of goods sold of ₦300,000, and other expenses of ₦120,000. Find the gross profit and net profit.
Gross profit = \(500{,}000 - 300{,}000 = 200{,}000\). Net profit = \(200{,}000 - 120{,}000 = 80{,}000\).

## The balance sheet

The balance sheet is a snapshot of the business's financial position at a specific date, listing assets (what it owns), liabilities (what it owes), and capital (the owner's stake) -- always balancing according to the accounting equation, \(Assets = Liabilities + Capital\).""",
        "related_topics": ["Accounting Fundamentals", "Company and Partnership Accounts"],
    },
    {
        "subject": "Accounting",
        "topic": "Branch and Control Accounts",
        "title": "Branch and Control Accounts",
        "summary": "How businesses account for separate branches, and how control accounts summarize and verify large numbers of individual customer/supplier accounts.",
        "glossary": [
            {"term": "Branch account", "definition": "an account recording the transactions and performance of a specific branch of a business"},
            {"term": "Control account", "definition": "a summary account that totals many individual accounts, used to verify the ledger and detect errors"},
            {"term": "Sales ledger control account", "definition": "a control account summarizing all individual debtor (customer) accounts in the sales ledger"},
        ],
        "content_md": r"""## Branch accounts

A business with multiple branches may keep a separate branch account for each one, tracking goods sent to the branch, sales made there, and expenses incurred, to assess each branch's individual performance -- useful for deciding which branches are thriving and which may need attention or closure.

## Control accounts

A control account is a summary account that totals the balances of many individual accounts of the same type, providing a quick cross-check on the ledger without needing to add up hundreds or thousands of individual balances by hand. The sales ledger control account summarizes all individual customer (debtor) balances; the purchases ledger control account summarizes all individual supplier (creditor) balances.

Example 1: A business has 200 individual customer accounts in its sales ledger. Explain why a sales ledger control account is useful here.
Rather than manually adding up all 200 individual customer balances every time a check is needed, the sales ledger control account keeps a running total of all sales, receipts, and adjustments affecting debtors as a whole. If this control account total doesn't match the sum of the 200 individual balances, it signals an error somewhere in the sales ledger that needs investigating -- a much faster check than manually re-totaling everything each time.""",
        "related_topics": ["Ledger, Journal, and Source Documents", "Manufacturing and Departmental Accounts"],
    },
]


def main():
    if len(sys.argv) < 2:
        print('Usage: python -u seed_lesson_notes.py "<DATABASE_URL>" [--dry-run]')
        sys.exit(1)
    database_url = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, connect_args=connect_args)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    inserted, updated = 0, 0
    for n in NOTES:
        existing = (
            db.query(LessonNote)
            .filter(LessonNote.subject == n["subject"], LessonNote.topic == n["topic"])
            .first()
        )
        if existing:
            existing.title = n["title"]
            existing.summary = n["summary"]
            existing.glossary = n["glossary"]
            existing.content_md = n["content_md"]
            existing.related_topics = n["related_topics"]
            existing.status = "draft"
            existing.updated_at = datetime.utcnow()
            updated += 1
            print(f"  update: {n['subject']} / {n['topic']}")
        else:
            db.add(LessonNote(
                subject=n["subject"], topic=n["topic"], title=n["title"], summary=n["summary"],
                glossary=n["glossary"], content_md=n["content_md"], related_topics=n["related_topics"],
                status="draft",
            ))
            inserted += 1
            print(f"  insert: {n['subject']} / {n['topic']}")

    if dry_run:
        db.rollback()
        print(f"\n[dry run] Would insert {inserted}, update {updated}. No changes made.")
    else:
        db.commit()
        print(f"\nDone: inserted {inserted}, updated {updated} lesson notes (all saved as 'draft' -- review and publish from Admin -> Lesson notes).")
    db.close()


if __name__ == "__main__":
    main()
