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
