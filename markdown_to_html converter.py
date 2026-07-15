"""
Markdown to HTML Converter

This module converts Markdown text to HTML format.
It supports common Markdown syntax including headers, bold, italic, 
lists, code blocks, links, and more.

Author: Python Developer
Date: 2026
"""

import re


class MarkdownToHTML:
    """
    A class to convert Markdown text to HTML format.
    
    Attributes:
        markdown_text (str): The input Markdown text to be converted
    """
    
    def __init__(self, markdown_text):
        """
        Initialize the MarkdownToHTML converter with Markdown text.
        
        Args:
            markdown_text (str): The Markdown text to convert
        """
        self.markdown_text = markdown_text
        self.html_text = ""
    
    def convert(self):
        """
        Main method to convert Markdown to HTML.
        Applies all conversion rules in the correct order.
        
        Returns:
            str: The converted HTML text
        """
        # Start with the original markdown text
        self.html_text = self.markdown_text
        
        # Apply conversions in specific order to avoid conflicts
        self.html_text = self._convert_code_blocks()
        self.html_text = self._convert_inline_code()
        self.html_text = self._convert_headers()
        self.html_text = self._convert_bold()
        self.html_text = self._convert_italic()
        self.html_text = self._convert_links()
        self.html_text = self._convert_images()
        self.html_text = self._convert_lists()
        self.html_text = self._convert_horizontal_rule()
        self.html_text = self._convert_blockquotes()
        self.html_text = self._wrap_paragraphs()
        
        return self.html_text
    
    def _convert_code_blocks(self):
        """
        Convert code blocks (triple backticks) to HTML <pre><code> tags.
        This must be done first to prevent other conversions inside code blocks.
        
        Pattern: ```language\ncode here\n```
        Converted to: <pre><code class="language-lang">code here</code></pre>
        """
        # Match triple backticks with optional language identifier
        pattern = r'```(\w+)?\n(.*?)\n```'
        
        def replace_code_block(match):
            language = match.group(1) or 'plaintext'
            code_content = match.group(2)
            # Escape HTML special characters in code
            code_content = self._escape_html(code_content)
            return f'<pre><code class="language-{language}">{code_content}</code></pre>'
        
        # Use DOTALL flag to make . match newlines
        return re.sub(pattern, replace_code_block, self.html_text, flags=re.DOTALL)
    
    def _convert_inline_code(self):
        """
        Convert inline code (single backticks) to HTML <code> tags.
        
        Pattern: `code here`
        Converted to: <code>code here</code>
        """
        # Match text between single backticks
        pattern = r'`([^`]+)`'
        replacement = r'<code>\1</code>'
        return re.sub(pattern, replacement, self.html_text)
    
    def _convert_headers(self):
        """
        Convert Markdown headers to HTML header tags.
        
        Patterns:
        # Heading 1 -> <h1>Heading 1</h1>
        ## Heading 2 -> <h2>Heading 2</h2>
        ... up to ######
        """
        # Process headers from h6 to h1 (larger numbers first to avoid conflicts)
        for level in range(6, 0, -1):
            # Create pattern for current heading level
            # Pattern: ^ followed by 'level' number of # and a space
            pattern = r'^' + '#' * level + r' (.+)$'
            replacement = f'<h{level}>\\1</h{level}>'
            # MULTILINE flag allows ^ and $ to match line boundaries
            self.html_text = re.sub(pattern, replacement, self.html_text, flags=re.MULTILINE)
        
        return self.html_text
    
    def _convert_bold(self):
        """
        Convert bold text to HTML <strong> tags.
        
        Patterns:
        **bold text** -> <strong>bold text</strong>
        __bold text__ -> <strong>bold text</strong>
        """
        # Pattern for **text** or __text__
        pattern = r'\*\*(.+?)\*\*|__(.+?)__'
        
        def replace_bold(match):
            # Get whichever group matched (group 1 or 2)
            text = match.group(1) or match.group(2)
            return f'<strong>{text}</strong>'
        
        return re.sub(pattern, replace_bold, self.html_text)
    
    def _convert_italic(self):
        """
        Convert italic text to HTML <em> tags.
        
        Patterns:
        *italic text* -> <em>italic text</em>
        _italic text_ -> <em>italic text</em>
        """
        # Pattern for *text* or _text_
        # Use negative lookbehind/lookahead to avoid matching ** or __
        pattern = r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)|(?<!_)_(?!_)(.+?)(?<!_)_(?!_)'
        
        def replace_italic(match):
            # Get whichever group matched (group 1 or 2)
            text = match.group(1) or match.group(2)
            return f'<em>{text}</em>'
        
        return re.sub(pattern, replace_italic, self.html_text)
    
    def _convert_links(self):
        """
        Convert Markdown links to HTML anchor tags.
        
        Pattern: [link text](url)
        Converted to: <a href="url">link text</a>
        """
        # Pattern: [text](url)
        pattern = r'\[(.+?)\]\((.+?)\)'
        replacement = r'<a href="\2">\1</a>'
        return re.sub(pattern, replacement, self.html_text)
    
    def _convert_images(self):
        """
        Convert Markdown images to HTML img tags.
        
        Pattern: ![alt text](image-url)
        Converted to: <img src="image-url" alt="alt text">
        """
        # Pattern: ![alt](url)
        # Note: This must come after link conversion to avoid conflicts
        pattern = r'!\[(.+?)\]\((.+?)\)'
        replacement = r'<img src="\2" alt="\1">'
        return re.sub(pattern, replacement, self.html_text)
    
    def _convert_lists(self):
        """
        Convert Markdown lists to HTML list tags.
        Supports both unordered (*,-, +) and ordered (1., 2., etc.) lists.
        
        Pattern for unordered: * item or - item or + item
        Pattern for ordered: 1. item, 2. item
        """
        lines = self.html_text.split('\n')
        result = []
        in_ul = False  # Track if we're inside an unordered list
        in_ol = False  # Track if we're inside an ordered list
        
        for line in lines:
            # Check for unordered list items
            if re.match(r'^[\*\-\+]\s', line):
                if not in_ul:
                    # Start a new unordered list
                    result.append('<ul>')
                    in_ul = True
                if in_ol:
                    # Close ordered list if it was open
                    result.append('</ol>')
                    in_ol = False
                
                # Extract list item content and wrap in <li>
                item_content = re.sub(r'^[\*\-\+]\s', '', line)
                result.append(f'<li>{item_content}</li>')
            
            # Check for ordered list items (1., 2., etc.)
            elif re.match(r'^\d+\.\s', line):
                if not in_ol:
                    # Start a new ordered list
                    result.append('<ol>')
                    in_ol = True
                if in_ul:
                    # Close unordered list if it was open
                    result.append('</ul>')
                    in_ul = False
                
                # Extract list item content and wrap in <li>
                item_content = re.sub(r'^\d+\.\s', '', line)
                result.append(f'<li>{item_content}</li>')
            
            else:
                # Line is not a list item
                if in_ul:
                    # Close unordered list
                    result.append('</ul>')
                    in_ul = False
                if in_ol:
                    # Close ordered list
                    result.append('</ol>')
                    in_ol = False
                
                # Add the line if it's not empty
                if line.strip():
                    result.append(line)
        
        # Close any open lists at the end
        if in_ul:
            result.append('</ul>')
        if in_ol:
            result.append('</ol>')
        
        return '\n'.join(result)
    
    def _convert_horizontal_rule(self):
        """
        Convert horizontal rules to HTML <hr> tags.
        
        Patterns:
        --- or *** or ___
        Converted to: <hr>
        """
        # Pattern: 3 or more hyphens, asterisks, or underscores
        pattern = r'^(\-{3,}|\*{3,}|_{3,})$'
        replacement = '<hr>'
        return re.sub(pattern, replacement, self.html_text, flags=re.MULTILINE)
    
    def _convert_blockquotes(self):
        """
        Convert Markdown blockquotes to HTML blockquote tags.
        
        Pattern: > quote text
        Converted to: <blockquote>quote text</blockquote>
        """
        lines = self.html_text.split('\n')
        result = []
        in_blockquote = False
        blockquote_content = []
        
        for line in lines:
            # Check if line starts with >
            if line.startswith('> '):
                if not in_blockquote:
                    # Start a new blockquote
                    in_blockquote = True
                
                # Remove the > and leading space
                content = line[2:]
                blockquote_content.append(content)
            
            else:
                # Line is not part of blockquote
                if in_blockquote:
                    # Close the blockquote
                    combined_content = ' '.join(blockquote_content)
                    result.append(f'<blockquote>{combined_content}</blockquote>')
                    blockquote_content = []
                    in_blockquote = False
                
                # Add the line if not empty
                if line.strip():
                    result.append(line)
        
        # Close any open blockquote at the end
        if in_blockquote:
            combined_content = ' '.join(blockquote_content)
            result.append(f'<blockquote>{combined_content}</blockquote>')
        
        return '\n'.join(result)
    
    def _wrap_paragraphs(self):
        """
        Wrap remaining text lines in HTML <p> (paragraph) tags.
        This handles plain text that hasn't been converted to other tags.
        """
        lines = self.html_text.split('\n')
        result = []
        
        for line in lines:
            # Skip empty lines and lines that are already HTML tags
            if line.strip() and not line.strip().startswith('<'):
                # Wrap in paragraph tags
                result.append(f'<p>{line.strip()}</p>')
            else:
                result.append(line)
        
        return '\n'.join(result)
    
    def _escape_html(self, text):
        """
        Escape HTML special characters to prevent injection.
        
        Converts:
        & -> &amp;
        < -> &lt;
        > -> &gt;
        " -> &quot;
        ' -> &#39;
        """
        escape_dict = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }
        
        for char, escape in escape_dict.items():
            text = text.replace(char, escape)
        
        return text


def create_html_document(html_content, title="Converted Markdown"):
    """
    Wrap HTML content in a complete HTML document with proper structure.
    
    Args:
        html_content (str): The HTML body content
        title (str): The title of the HTML document
    
    Returns:
        str: A complete HTML document
    """
    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 20px;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin-left: 0;
            padding-left: 15px;
            color: #555;
        }}
        ul, ol {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        hr {{
            border: none;
            height: 1px;
            background-color: #ddd;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""
    return html_doc


# Example usage and demonstration
if __name__ == "__main__":
    # Sample markdown text for testing
    sample_markdown = """# Welcome to Markdown to HTML Converter

This is a **bold** text and this is *italic* text.

## Features

- Convert headers (h1 to h6)
- Bold and italic text
- Lists (ordered and unordered)
- Code blocks and inline code
- Links and images
- Blockquotes

### Code Example

Here's some inline `code` in a sentence.

And here's a code block:

```python
def hello_world():
    print("Hello, World!")
```

### Links and Images

Check out [Python](https://www.python.org) for more info.

![Python Logo](https://www.python.org/static/community_logos/python-logo.png)

### Blockquote

> This is a blockquote. It can contain multiple lines and should be properly formatted.

### Horizontal Rule

---

### Lists Example

Unordered list:
- Item 1
- Item 2
- Item 3

Ordered list:
1. First item
2. Second item
3. Third item
"""
    
    # Create converter instance
    converter = MarkdownToHTML(sample_markdown)
    
    # Convert markdown to HTML
    html_output = converter.convert()
    
    # Create a complete HTML document
    complete_html = create_html_document(html_output, "Markdown to HTML Conversion Demo")
    
    # Print the result (truncated for display)
    print("HTML Output:")
    print("=" * 50)
    print(complete_html)
    
    # Save to file
    with open('output.html', 'w', encoding='utf-8') as f:
        f.write(complete_html)
    
    print("\n" + "=" * 50)
    print("HTML file saved as 'output.html'")
