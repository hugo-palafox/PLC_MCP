import requests
import json
import re
import logging

logger = logging.getLogger("plc-bridge.ai-viz")

class AIVisualizationGenerator:
    """Generate dashboard visualizations using DeepSeek."""
    
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.2"  # Faster model for real-time generation
    
    def generate_visualization(self, user_query, metrics_data):
        """
        Generate HTML/CSS/JS code for visualization.
        
        Args:
            user_query: User's request (e.g., "Show OEE as gauge")
            metrics_data: Dict of metric values
        
        Returns:
            Dict with 'html', 'css', 'js' keys
        """
        logger.info(f"Generating AI visualization for: {user_query}")
        prompt = self._build_prompt(user_query, metrics_data)
        response = self._query_ollama(prompt)
        code = self._extract_code(response)
        code = self.sanitize_code(code)
        return code
    
    def _build_prompt(self, user_query, metrics_data):
        """Build prompt for DeepSeek."""
        # Simplified prompt for faster generation
        return f"""Generate HTML/CSS/JavaScript code to visualize this PLC data.

USER REQUEST: {user_query}

DATA:
{json.dumps(metrics_data, indent=2)}

Return ONLY code in this format (no explanations):

```html
<div class="viz">
  <!-- your HTML -->
</div>
```

```css
.viz {{
  /* your CSS */
  padding: 2rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
}}
```

```javascript
// your JavaScript (optional)
// vizContainer variable is available
```

Use dark theme (#0f0f23 bg), Chart.js available, colors: #667eea (primary), #10b981 (success), #ef4444 (danger).
Generate code now:"""
    
    def _query_ollama(self, prompt):
        """Query Ollama API."""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 2000
                    }
                },
                timeout=120  # Increased timeout for DeepSeek generation
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
            raise
    
    def _extract_code(self, response):
        """Extract HTML/CSS/JS from AI response."""
        # Extract code blocks
        html_match = re.search(r'```html\n(.*?)\n```', response, re.DOTALL)
        css_match = re.search(r'```css\n(.*?)\n```', response, re.DOTALL)
        js_match = re.search(r'```javascript\n(.*?)\n```', response, re.DOTALL)
        
        html = html_match.group(1).strip() if html_match else ''
        css = css_match.group(1).strip() if css_match else ''
        js = js_match.group(1).strip() if js_match else ''
        
        # Fallback: try to extract any code if structured format not found
        if not html:
            # Look for div tags
            div_match = re.search(r'(<div.*?</div>)', response, re.DOTALL)
            if div_match:
                html = div_match.group(1)
        
        return {
            'html': html,
            'css': css,
            'js': js,
            'raw_response': response
        }
    
    def sanitize_code(self, code):
        """Basic security checks."""
        dangerous_patterns = [
            (r'\beval\s*\(', 'eval() is not allowed'),
            (r'\bFunction\s*\(', 'Function() constructor is not allowed'),
            (r'<script[^>]*src\s*=', 'External scripts are not allowed'),
            (r'\bfetch\s*\(', 'fetch() is not allowed'),
            (r'\bXMLHttpRequest\b', 'XMLHttpRequest is not allowed'),
            (r'\bimport\s+', 'import statements are not allowed'),
            (r'\.innerHTML\s*=.*<script', 'Script injection detected'),
        ]
        
        combined_code = f"{code.get('html', '')} {code.get('js', '')}"
        
        for pattern, message in dangerous_patterns:
            if re.search(pattern, combined_code, re.IGNORECASE):
                logger.warning(f"Security check failed: {message}")
                raise ValueError(f"Security violation: {message}")
        
        return code
