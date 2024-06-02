SUMMARIZE_PROMPT_TEMPLATE = """
You are an expert researcher, summarize the key points of the given paper.

===================================
If the paper is a research paper, the summary should include the following sections:

Introduction:

- Briefly describe the context and motivation for the study.
- What problem or question does the paper address?

Methods:

- Outline the methodology used in the study.
- What approach or techniques were used to address the problem?

Results:

- Summarize the main findings or results of the study.
- What are the key outcomes?

Discussion:

- Interpret the significance of the results.
- How do the findings contribute to the field?
- Are there any limitations mentioned?

Conclusion:

- Summarize the main conclusions of the paper.
- What future directions or questions do the authors suggest?

===================================
If the paper is a Survey paper, the summary should include the following sections:

Introduction and Motivation:

- What is the background and context of this survey?
- What motivated the authors to conduct this survey?
- Why is this survey significant in its field?

Scope of the Survey:

- What specific topics, technologies, methods, or trends does this survey cover?
- Are there any specific boundaries or limitations to what is included in the survey?

Classification and Taxonomy:

- Does the survey provide a classification scheme or taxonomy? If so, what is it?
- What are the main categories or groups identified in the survey?

Literature Review:

- Which key studies, papers, or contributions are highlighted in the survey?
- What trends, patterns, and emerging themes are identified from the literature?

Comparative Analysis:

- How are different approaches, methods, or technologies compared in the survey?
- What are the pros and cons of these various approaches?

Methodologies and Techniques:

- What common methodologies and techniques are discussed?
- Are there any novel or innovative methods mentioned in the survey?


Applications and Implications:

- What are the practical applications of the surveyed technologies or methods?
- What are the implications of the survey findings for practice and future research?


Challenges and Open Issues:

- What are the current challenges or limitations identified in the field?
- What research gaps and potential areas for future research are pointed out?

Conclusions and Future Directions:

- What are the main findings summarized in the survey?
- What directions for future research and development do the authors suggest?

References:

- What are some of the most important references cited in the survey, particularly those seminal to the field?


####
Here is the paper content

{content}

"""