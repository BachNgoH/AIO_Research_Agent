SOURCE_CONTAINER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Styled Containers in Row</title>
    <style>
        .master-container {{
            display: flex;
            flex-direction: row;
            gap: 10px; /* Space between items */
            padding: 10px;
            background-color: #f0f0f0;
            overflow-x: auto; /* Enable horizontal scrolling */
        }}
        .container {{
            display: flex;
            align-items: start;
            flex-direction: column;
            justify-content: center;
            padding: 10px;
            background-color: #f9fafb;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            font-family: Arial, sans-serif;
            color: #39434d;
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
            background-color: #e6e6e6;
            border-radius: 5%;
            padding-top: 5px;
            padding-bottom: 5px;
            padding-right: 15px;
            padding-left: 15px;
            
            font-size: 12px;
            color: #39434d;
            height: 20px; /* Fixed height */
            margin-top: 5px; /* Space between badge and text */
        }}
        a {{
            text-decoration: none; /* Remove underline from links */
            color: inherit; /* Inherit color from parent */
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