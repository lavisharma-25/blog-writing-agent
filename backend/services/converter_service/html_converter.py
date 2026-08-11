import re
import html


def md_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    body: list[str] = []
    in_list = False
    in_code = False

    for line in lines:
        if line.strip().startswith("```"):
            if in_code:
                body.append("</code></pre>")
            else:
                body.append("<pre><code>")
            in_code = not in_code
            continue

        if in_code:
            body.append(html.escape(line))
            continue

        heading = re.match(r"^(#{1,3})\s+(.*)$", line)
        item = re.match(r"^[-*]\s+(.*)$", line)

        if heading:
            if in_list:
                body.append("</ul>")
                in_list = False
            level = len(heading.group(1))
            body.append(f"<h{level}>{html.escape(heading.group(2))}</h{level}>")
        elif item:
            if not in_list:
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{html.escape(item.group(1))}</li>")
        elif line.strip():
            if in_list:
                body.append("</ul>")
                in_list = False
            body.append(f"<p>{html.escape(line)}</p>")

    if in_list:
        body.append("</ul>")
    if in_code:
        body.append("</code></pre>")

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>Generated Blog</title>",
            "</head>",
            "<body>",
            *body,
            "</body>",
            "</html>",
        ]
    )
