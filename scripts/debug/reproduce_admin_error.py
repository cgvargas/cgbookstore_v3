from django.utils.html import format_html, conditional_escape

try:
    score = 0.95
    # Simulating what happens inside format_html roughly, but calling it directly is better test
    print(f"Testing format_html with float and percent format...")
    result = format_html(
        '<span>{:.0%}</span>',
        score
    )
    print(f"Result: {result}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

# Proposed fix simulation
try:
    print(f"\nTesting proposed fix...")
    score = 0.95
    formatted_score = f"{score:.0%}"
    result = format_html(
        '<span>{}</span>',
        formatted_score
    )
    print(f"Result: {result}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
