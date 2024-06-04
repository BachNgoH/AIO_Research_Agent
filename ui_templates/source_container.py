# --background-color: #f0f0f0;  
# --container-background: #f9fafb; 
# --text-color: #39434d;
# --badge-background: #e6e6e6;
# --link-color: #4285f4; /* Example of a contrasting link color */

SOURCE_CONTAINER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Styled Containers in Row</title>
    <style>
        /* Custom scrollbar for WebKit browsers */
        ::-webkit-scrollbar {{
            width: 8px;  /* Width of the scrollbar */
            height: 8px; /* Height of the scrollbar (for horizontal scrollbars) */
        }}

        ::-webkit-scrollbar-thumb {{
            background: #888; /* Color of the scrollbar thumb */
            border-radius: 10px; /* Rounded corners for the scrollbar thumb */
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #555; /* Color of the scrollbar thumb when hovered */
        }}

        ::-webkit-scrollbar-track {{
            background: #121212; /* Color of the scrollbar track */
        }}

        :root {{
            --background-color: #121212; 
            --container-background: #1e1e1e;
            --text-color: #e8eaed;
            --badge-background: #303030;
            --link-color: #8ab4f8; /* Lighter link for contrast */
        }}


        /* Dark Mode Styles */
        body.dark-mode {{
            --background-color: #121212; 
            --container-background: #1e1e1e;
            --text-color: #e8eaed;
            --badge-background: #303030;
            --link-color: #8ab4f8; /* Lighter link for contrast */
        }}

        .master-container {{
            display: flex;
            flex-direction: row;
            gap: 10px; 
            padding: 10px;
            background-color: var(--background-color); 
            overflow-x: scroll; 
        }}
        .container {{
            display: flex;
            align-items: start;
            flex-direction: column;
            justify-content: center;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            font-family: Arial, sans-serif;
            background-color: var(--container-background);
            color: var(--text-color);
            min-width: 250px; /* Minimum width to maintain layout */
        }}
        .icon {{
            width: 20px;
            height: 20px;
            margin-right: 10px;
        }}
        .text {{
            flex-grow: 1;
            font-size: 14px;
        }}
        .badge {{
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 5%;
            padding-top: 5px;
            padding-bottom: 5px;
            padding-right: 15px;
            padding-left: 15px;
            
            font-size: 12px;
            background-color: var(--badge-background);
            color: var(--text-color);
            height: 20px; /* Fixed height */
            margin-top: 5px; /* Space between badge and text */
        }}
        a {{
            text-decoration: none; /* Remove underline from links */
            color: var(--link-color); 
        }}
        .favicon {{
            width: 16px;  /* Fixed width for the favicon */
            height: 16px; /* Fixed height for the favicon */
            margin-right: 5px;  /* Space between favicon and text */
        }}
    </style>
</head>
<body>
    <div class="master-container">{}
    </div>
    <script>
        console.log("Loaded theme");

        (function() {{ 
            function loadTheme() {{
                const themeVariant = localStorage.getItem('themeVariant'); // Get stored theme
                console.log("Theme variant: ", themeVariant);
                if (themeVariant === 'dark') {{
                    document.body.classList.add('dark-mode'); // Apply dark mode
                }} else {{
                    document.body.classList.remove('dark-mode'); // Apply light mode (or remove dark mode)
                }}
            }}
        
            loadTheme();
        }})();
        
    </script>
</body>
</html>

"""


SOURCE_NODE_CONTENT_TEMPLATE = """
        <a href="{link}" class="container">
            <div class="text">{title}</div>
            <div class="badge">
                <img src="{web_favicon}" alt="favicon" class="favicon">
                {web_name}
            </div>
        </a>"""