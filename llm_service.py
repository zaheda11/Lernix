import json
import requests
import re
import random

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "granite3.3:latest" # Configured for IBM Granite 3.3

def generate_curriculum_from_llm(title, field, duration, target_audience="Undergraduate"):
    """
    Asks the local Ollama LLM to generate a full structured curriculum in JSON.
    Falls back to mock data if Ollama is unavailable or fails to output correct JSON.
    """
    prompt = f"""
    You are an expert Educational Technology Architect. Generate a complete, industry-aligned semester-wise curriculum.
    
    Details:
    - Title: {title}
    - Field of Study: {field}
    - Duration: {duration} Semesters
    - Target Audience: {target_audience}
    
    You must output a single JSON object. Do not wrap the JSON in ```json``` blocks. Do not add any conversational text before or after the JSON.
    
    JSON Schema:
    {{
      "title": "{title}",
      "field_of_study": "{field}",
      "duration_semesters": {duration},
      "semesters": [
        {{
          "semester_number": 1,
          "courses": [
            {{
              "code": "CS-101",
              "name": "Course Name",
              "description": "Course description (at least 2 sentences)",
              "credits": 4,
              "learning_outcomes": ["outcome 1", "outcome 2"],
              "prerequisites": [],
              "assessment_methods": ["Midterm Exam: 30%", "Final Exam: 40%", "Lab Work: 30%"],
              "difficulty": "Beginner|Intermediate|Advanced",
              "learning_time_weeks": 15,
              "weekly_hours": 6,
              "industry_relevance_score": 95,
              "career_opportunities": ["Job Title 1", "Job Title 2"],
              "recommended_projects": ["Project Idea 1"],
              "key_skills": ["Skill 1", "Skill 2"]
            }}
          ]
        }}
      ]
    }}
    
    Make sure:
    - Every semester has exactly 3-4 courses.
    - Course prerequisites refer to course names/codes from previous semesters.
    - Realistic difficulty level, credits (3 or 4), learning hours, and career opportunities.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": DEFAULT_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            },
            timeout=15
        )
        if response.status_code == 200:
            raw_text = response.json().get("response", "").strip()
            cleaned_text = re.sub(r"^```json\s*", "", raw_text, flags=re.MULTILINE)
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text, flags=re.MULTILINE).strip()
            
            parsed_json = json.loads(cleaned_text)
            
            # Post-process to ensure course-level resources are set
            for sem in parsed_json.get("semesters", []):
                for course in sem.get("courses", []):
                    if "resources" not in course or not course["resources"]:
                        skills = course.get("key_skills", ["IT"])
                        skill_name = skills[0] if skills else "Technology"
                        course_name_url = course.get('name', 'course').replace(' ', '+')
                        course["resources"] = [
                            {"title": f"ACM/IEEE Guidelines on {course.get('name', 'this course')}", "url": f"https://www.acm.org/search?q={course_name_url}"},
                            {"title": f"IBM Cognitive Class: {skill_name}", "url": f"https://cognitiveclass.ai/courses?search={skill_name.replace(' ', '+')}"}
                        ]
            
            parsed_json["resource_sources"] = [
                "ACM/IEEE Joint Curriculum Guidelines",
                "IBM Skills Network Course Frameworks",
                "Hugging Face Applied NLP Curriculum",
                "LERNIX AI Engine via Granite 3.3 2B"
            ]
            return parsed_json
    except Exception as e:
        print(f"Ollama connection or execution failed: {e}. Falling back to high-quality mock curriculum.")
        
    return generate_mock_curriculum(title, field, duration)

def generate_study_plan_from_llm(curriculum_title, course_name, weekly_hours=10):
    """
    Asks the Ollama LLM to generate a customized study plan for a particular course.
    Falls back to mock data if Ollama is unavailable.
    """
    prompt = f"""
    You are an AI Student Assistant. Generate a structured student study guide and schedule for the course: "{course_name}" which belongs to the curriculum "{curriculum_title}".
    The student can dedicate {weekly_hours} hours per week.
    
    Output a single JSON object. Do not wrap in markdown syntax. Do not output anything other than raw JSON.
    
    JSON Schema:
    {{
      "course_name": "{course_name}",
      "weekly_hours_allocated": {weekly_hours},
      "weekly_schedule": [
        {{
          "week": 1,
          "topic": "Topic Name",
          "tasks": ["Study concept X (3 hrs)", "Watch video tutorial Y (2 hrs)", "Practice lab Z (5 hrs)"],
          "resources": [
             {{"title": "Resource Name", "url": "https://example.com/topic"}}
          ],
          "milestone": "Milestone description"
        }}
      ],
      "revision_roadmap": [
        {{
          "phase": "Phase 1: Foundation",
          "timeline": "Weeks 1-4",
          "focus": "Core principles",
          "checkpoints": ["Checkpoint 1"]
        }}
      ],
      "interview_preparation": [
        {{
          "topic": "Core Concept X",
          "sample_questions": [
            {{
              "question": "Sample interview question?",
              "answer": "Accurate, concise industry answer."
            }}
          ]
        }}
      ]
    }}
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": DEFAULT_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.4
                }
            },
            timeout=15
        )
        if response.status_code == 200:
            raw_text = response.json().get("response", "").strip()
            cleaned_text = re.sub(r"^```json\s*", "", raw_text, flags=re.MULTILINE)
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text, flags=re.MULTILINE).strip()
            
            parsed_json = json.loads(cleaned_text)
            parsed_json["resource_sources"] = [
                "LeetCode Interview Guides",
                "GeeksforGeeks Academic Prep Sheets",
                "O'Reilly Learning Pathways",
                "LERNIX Student Assistant Agent"
            ]
            return parsed_json
    except Exception as e:
        print(f"Ollama study plan failed: {e}. Falling back to mock assistant data.")
        
    return generate_mock_study_plan(course_name, weekly_hours)

def generate_custom_interview_answer(course_name, question):
    """
    Queries Ollama to answer a custom student question about a course.
    Falls back to a structured mock answer if Ollama is unreachable.
    """
    q_lower = question.lower()

    # Relevance gate: reject off-topic questions
    course_keywords = set(course_name.lower().split())
    # Question must have BOTH a question word AND a technical/academic subject term
    question_words = {"what", "how", "why", "explain", "define", "difference", "compare", "describe", "is", "are", "does"}
    technical_words = {
        "algorithm", "function", "class", "method", "variable", "data", "type",
        "loop", "array", "list", "object", "model", "network", "database", "query",
        "api", "design", "pattern", "complexity", "sort", "search", "tree", "graph",
        "stack", "queue", "pointer", "memory", "process", "thread", "security",
        "encrypt", "protocol", "syntax", "compile", "debug", "test", "deploy",
        "framework", "library", "module", "concept", "principle", "implement",
        "agile", "scrum", "obe", "outcome", "prerequisite", "curriculum",
        "machine", "learning", "neural", "regression", "cluster", "cloud",
        "tuple", "integer", "string", "boolean", "inheritance", "polymorphism",
        "recursion", "iteration", "index", "hash", "binary", "sql", "nosql",
        "http", "rest", "json", "xml", "python", "java", "javascript", "c++"
    }
    q_words = set(q_lower.split())
    has_question_word = bool(q_words & question_words)
    has_technical_word = bool(q_words & technical_words) or bool(q_words & course_keywords)
    if not (has_question_word and has_technical_word):
        return "Sorry, I can't answer that. Please ask a question related to your course or academic topic."

    # Predefined high-quality answers for common topics
    common_qa_map = {
        "tuple": "In Python, lists are mutable (can be altered in-place), whereas tuples are immutable. Lists use square brackets `[]` while tuples use parentheses `()`. Tuples are faster and safer for write-protected data.",
        "complexity": "The average time complexity of searching in a Hash Table is O(1). This is achieved via a hash function mapping keys to bucket indices. Worst-case degrades to O(n) under severe collisions.",
        "hash table": "The average time complexity of searching in a Hash Table is O(1). This is achieved via a hash function mapping keys to bucket indices. Worst-case degrades to O(n) under severe collisions.",
        "self": "In Python, `self` represents the current instance of the class. It binds attributes and methods to the specific object, allowing access to instance variables within the class definition.",
        "obe": "Outcome-Based Education (OBE) structures curriculum backward from desired graduate competencies, directly aligning learning activities and assessments to verify student capabilities.",
        "outcome-based": "Outcome-Based Education (OBE) structures curriculum backward from desired graduate competencies, directly aligning learning activities and assessments to verify student capabilities.",
        "prerequisite": "A prerequisite is a foundational course that must be completed before enrolling in a more advanced course, ensuring students have the required background knowledge.",
        "agile": "An Agile iteration is a short time-boxed cycle (1-4 weeks) where a team designs, builds, and tests a working product increment, enabling continuous inspection and adaptation."
    }

    for key, ans in common_qa_map.items():
        if key in q_lower:
            return ans

    # Try Ollama
    prompt = f"""You are LERNIX AI tutor. Answer the student's interview preparation question about the course '{course_name}'.
Question: {question}
Provide a concise, technically accurate response of maximum 4 sentences."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": DEFAULT_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.4}},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except Exception:
        pass

    # Heuristic fallback — only for genuinely academic questions (already passed relevance gate)
    if "how" in q_lower or "explain" in q_lower:
        return f"In {course_name}, this concept is implemented by establishing core environment parameters, writing modular functions, and performing unit verification to guarantee scalability."
    elif "difference" in q_lower or "vs" in q_lower:
        return f"The key difference lies in resource efficiency and data isolation. One approach provides direct access while the other ensures thread safety and security at a minor performance cost."
    else:
        return f"In {course_name}, this is addressed by declaring clean abstractions, validating inputs, handling errors structurally, and following industry coding standards."

def generate_course_quiz(course_name):
    """
    Returns 3 structured quiz questions for a course.
    """
    # Pre-defined high-quality quiz pools for CS and other topics
    c_lower = course_name.lower()
    if "python" in c_lower or "programming" in c_lower:
        return [
            {
                "question": "Which of the following data types in Python is immutable?",
                "options": ["List", "Dictionary", "Tuple", "Set"],
                "correct_index": 2,
                "explanations": [
                    "Incorrect. Lists are mutable and can be changed in-place.",
                    "Incorrect. Dictionaries are mutable; keys/values can be modified.",
                    "Correct! Tuples are immutable sequences in Python.",
                    "Incorrect. Sets are mutable (although their elements must be hashable)."
                ]
            },
            {
                "question": "What does the 'self' keyword represent in a Python class?",
                "options": [
                    "The class object itself",
                    "The current instance of the class",
                    "A global variable declaration",
                    "A parent class initializer"
                ],
                "correct_index": 1,
                "explanations": [
                    "Incorrect. 'self' points to the specific instance, not the class definition.",
                    "Correct! 'self' references the current object instance being manipulated.",
                    "Incorrect. 'self' has local scope within object methods.",
                    "Incorrect. Parent initializers are accessed via super()."
                ]
            },
            {
                "question": "What is the primary use of a 'list comprehension' in Python?",
                "options": [
                    "To compress lists for network transfers",
                    "To document lists using docstrings",
                    "To generate a new list from an existing sequence in a single line",
                    "To sort lists in reverse order"
                ],
                "correct_index": 2,
                "explanations": [
                    "Incorrect. It does not perform file or byte stream compression.",
                    "Incorrect. Docstrings are used for class/method documentation.",
                    "Correct! List comprehensions offer a concise way to create lists.",
                    "Incorrect. reverse=True is used in the sort() method."
                ]
            }
        ]
    elif "data structures" in c_lower or "algorithms" in c_lower:
        return [
            {
                "question": "What is the average time complexity of searching in a Hash Table?",
                "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                "correct_index": 0,
                "explanations": [
                    "Correct! On average, hash table operations achieve constant O(1) complexity.",
                    "Incorrect. O(log n) corresponds to balanced tree lookups.",
                    "Incorrect. O(n) is the linear worst-case under severe hash collisions.",
                    "Incorrect. O(n log n) is sorting complexity (e.g. merge sort)."
                ]
            },
            {
                "question": "Which data structure follows the First-In, First-Out (FIFO) principle?",
                "options": ["Stack", "Queue", "Binary Tree", "Graph"],
                "correct_index": 1,
                "explanations": [
                    "Incorrect. Stacks use LIFO (Last-In, First-Out).",
                    "Correct! Queues are FIFO structures where elements enter at the rear and exit at the front.",
                    "Incorrect. Trees are hierarchical structures, not simple FIFO buffers.",
                    "Incorrect. Graphs are non-linear networks."
                ]
            },
            {
                "question": "Which sorting algorithm has a guaranteed worst-case time complexity of O(n log n)?",
                "options": ["Bubble Sort", "Quick Sort", "Merge Sort", "Insertion Sort"],
                "correct_index": 2,
                "explanations": [
                    "Incorrect. Bubble Sort has O(n^2) worst-case complexity.",
                    "Incorrect. Quick Sort averages O(n log n) but degrades to O(n^2) in worst case.",
                    "Correct! Merge Sort uses divide-and-conquer to guarantee O(n log n) in all cases.",
                    "Incorrect. Insertion Sort has O(n^2) worst-case complexity."
                ]
            }
        ]
    else:
        # Default quiz questions for generic courses
        return [
            {
                "question": "What is the primary objective of applying Outcome-Based Education (OBE)?",
                "options": [
                    "To increase university revenue stream",
                    "To align curriculum plans directly with measurable student competencies",
                    "To eliminate mid-term exam sheets",
                    "To automate professor classroom grading"
                ],
                "correct_index": 1,
                "explanations": [
                    "Incorrect. Revenue generation is not an academic pedagogy.",
                    "Correct! OBE designs curriculums backwards starting from desired graduate outcomes.",
                    "Incorrect. Exams are still utilized as validation methods.",
                    "Incorrect. It does not replace manual grading workloads."
                ]
            },
            {
                "question": "Which element represents a 'Prerequisite' in academic paths?",
                "options": [
                    "A course that must be completed BEFORE taking another course",
                    "A tool for printing PDF certificates",
                    "The final project score card",
                    "A list of career opportunities"
                ],
                "correct_index": 0,
                "explanations": [
                    "Correct! Prerequisites establish the required foundational knowledge.",
                    "Incorrect. PDFs are generated via ReportLab.",
                    "Incorrect. That is an assessment method.",
                    "Incorrect. Career opportunities describe graduation jobs."
                ]
            },
            {
                "question": "In project design, what does 'Agile iteration' mean?",
                "options": [
                    "Completing all code in a single marathon sprint",
                    "Writing code without checking console errors",
                    "Working in short, repetitive cycles to inspect and adapt product increments",
                    "Delegating all tasks to artificial intelligence agents"
                ],
                "correct_index": 2,
                "explanations": [
                    "Incorrect. Agile promotes incremental pacing, not single runs.",
                    "Incorrect. Error checking is critical in all loops.",
                    "Correct! Agile iterations are designed for incremental feedbacks.",
                    "Incorrect. AI tools assist developers but do not run Agile scopes."
                ]
            }
        ]

def generate_capstone_guidelines(curriculum_title, field, courses_summary):
    """
    Generates a structured capstone project guideline for the full curriculum.
    Falls back to a high-quality mock if Ollama is unavailable.
    """
    prompt = f"""You are an academic curriculum expert. Generate a detailed capstone project guideline for a curriculum titled "{curriculum_title}" in the field of "{field}".

Courses covered: {courses_summary}

Output a single JSON object only. No markdown, no extra text.

JSON Schema:
{{
  "title": "Capstone Project Title",
  "overview": "2-3 sentence project overview",
  "objectives": ["objective 1", "objective 2", "objective 3"],
  "deliverables": [
    {{"name": "Deliverable Name", "description": "What must be submitted"}}
  ],
  "milestones": [
    {{"phase": "Phase Name", "duration": "X weeks", "tasks": ["task 1", "task 2"]}}
  ],
  "evaluation_criteria": [
    {{"criterion": "Criterion Name", "weight": "X%", "description": "How it is assessed"}}
  ],
  "recommended_tools": ["Tool 1", "Tool 2"],
  "suggested_topics": ["Topic idea 1", "Topic idea 2", "Topic idea 3"]
}}"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": DEFAULT_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.3}},
            timeout=15
        )
        if response.status_code == 200:
            raw = response.json().get("response", "").strip()
            raw = re.sub(r"^```json\s*", "", raw, flags=re.MULTILINE)
            raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE).strip()
            return json.loads(raw)
    except Exception as e:
        print(f"Capstone generation failed: {e}")
    return _mock_capstone(curriculum_title, field)

def _mock_capstone(title, field):
    return {
        "title": f"Capstone Project: {title}",
        "overview": f"This capstone project challenges students to integrate all concepts learned across the {title} curriculum into a single, deployable, industry-grade solution in the domain of {field}.",
        "objectives": [
            "Apply theoretical knowledge to a real-world problem",
            "Demonstrate full-stack or end-to-end system design skills",
            "Produce professional documentation and a working prototype",
            "Present findings to a panel of evaluators"
        ],
        "deliverables": [
            {"name": "Project Proposal", "description": "1-2 page document outlining problem statement, objectives, and tech stack"},
            {"name": "Working Prototype", "description": "Functional application or model meeting defined requirements"},
            {"name": "Technical Report", "description": "10-15 page report covering architecture, implementation, and evaluation"},
            {"name": "Final Presentation", "description": "15-minute demo and Q&A session with evaluators"}
        ],
        "milestones": [
            {"phase": "Research & Planning", "duration": "2 weeks", "tasks": ["Define problem scope", "Review literature", "Select technology stack"]},
            {"phase": "Design & Architecture", "duration": "2 weeks", "tasks": ["Create system diagrams", "Define data models", "Set up project repository"]},
            {"phase": "Implementation", "duration": "4 weeks", "tasks": ["Build core features", "Integrate components", "Write unit tests"]},
            {"phase": "Testing & Refinement", "duration": "1 week", "tasks": ["User acceptance testing", "Bug fixes", "Performance optimization"]},
            {"phase": "Documentation & Presentation", "duration": "1 week", "tasks": ["Finalize report", "Prepare slides", "Record demo video"]}
        ],
        "evaluation_criteria": [
            {"criterion": "Technical Complexity", "weight": "30%", "description": "Depth of implementation and appropriate use of course concepts"},
            {"criterion": "Functionality", "weight": "25%", "description": "Working prototype meeting all defined requirements"},
            {"criterion": "Documentation Quality", "weight": "20%", "description": "Clarity, completeness, and professional standard of written report"},
            {"criterion": "Presentation & Defence", "weight": "15%", "description": "Clear communication and ability to answer questions"},
            {"criterion": "Innovation", "weight": "10%", "description": "Originality and creative problem-solving approach"}
        ],
        "recommended_tools": ["Git / GitHub", "VS Code", "Docker", "Postman", "Figma", "Jupyter Notebook"],
        "suggested_topics": [
            f"AI-powered {field} recommendation system",
            f"Full-stack {field} management platform",
            f"Data analytics dashboard for {field} metrics"
        ]
    }



def generate_mock_curriculum(title, field, duration):
    """
    Generates realistic, highly structured curricula based on keywords in title/field.
    """
    duration = int(duration)
    field_lower = field.lower()
    title_lower = title.lower()
    combined = field_lower + " " + title_lower

    if any(k in combined for k in ["computer", "software", "programming", "engineering", "web", "mobile", "backend", "frontend"]):
        topic_pool = [
            ("CS101", "Introduction to Python Programming", "Fundamental control flows, variables, data structures (lists, dicts), and writing clean modular programs in Python.", 3, "Beginner", 90, ["Python Developer"], ["CLI Calculator", "Contact Book App"], ["Python", "Algorithms"]),
            ("CS102", "Object-Oriented Design", "Advanced concepts of OOP including encapsulation, inheritance, polymorphism, design patterns, and UML diagramming.", 4, "Beginner", 88, ["Software Intern"], ["Library Management System"], ["OOP", "UML"]),
            ("CS201", "Data Structures & Algorithms", "Detailed study of arrays, linked lists, stacks, queues, trees, graphs, sorting/searching algorithms, and big-O time complexity analysis.", 4, "Intermediate", 95, ["Backend Engineer"], ["Maze Solver using DFS/BFS"], ["Data Structures", "Algorithms"]),
            ("CS202", "Database Management Systems", "Relational database concepts, SQL query optimization, database design principles (normalization), and intro to NoSQL databases.", 3, "Intermediate", 92, ["Database Administrator", "Backend Developer"], ["E-commerce Database Design"], ["SQL", "Relational DB"]),
            ("CS301", "Web Development & APIs", "Full-stack development foundations. Front-end HTML/CSS/JS alongside backend Flask server creation, REST APIs, and AJAX requests.", 4, "Intermediate", 96, ["Full-Stack Developer"], ["Social Media API clone"], ["JavaScript", "APIs", "Flask"]),
            ("CS302", "Artificial Intelligence Foundations", "Foundations of AI, machine learning pipelines, regression, classification, clustering, neural networks, and prompt engineering.", 4, "Advanced", 98, ["AI Engineer", "ML Practitioner"], ["Spam Email Classifier", "Gemini API Assistant"], ["Machine Learning", "Neural Networks"]),
            ("CS401", "Software Engineering & Devops", "Agile methodologies, testing (unit, integration), version control with Git, CI/CD pipelines, Docker containerization, and cloud deployment.", 4, "Advanced", 94, ["DevOps Engineer", "Release Engineer"], ["Automated CI/CD Pipeline deployment"], ["Docker", "CI/CD", "Git"]),
            ("CS402", "Cybersecurity & Networks", "Fundamentals of computer networks, TCP/IP stack, encryption algorithms, hashing, public key cryptography, and common web security threats.", 3, "Advanced", 93, ["Security Consultant", "Network Analyst"], ["Secure File Transfer Utility"], ["Encryption", "Security"])
        ]
    elif any(k in combined for k in ["data", "analytics", "science", "machine learning", "ml", "statistics", "ai", "artificial", "neural", "deep learning"]):
        topic_pool = [
            ("DS101", "Foundations of Data Science", "Introduction to Jupyter Notebooks, Pandas, Numpy, data cleaning, and basic exploratory data analysis (EDA).", 3, "Beginner", 94, ["Data Analyst"], ["Exploratory Analysis of Housing Market"], ["Pandas", "Python"]),
            ("DS102", "Applied Probability & Statistics", "Probability theory, random variables, hypothesis testing, ANOVA, linear regression, and statistical inference.", 4, "Beginner", 90, ["Junior Statistician"], ["A/B Testing Simulator"], ["Statistics", "R"]),
            ("DS201", "Data Visualization Techniques", "Creating impactful visualizations using Matplotlib, Seaborn, Tableau, and Chart.js. Storytelling with data.", 3, "Intermediate", 91, ["BI Analyst"], ["Interactive COVID-19 Dashboard"], ["Tableau", "Chart.js"]),
            ("DS202", "Machine Learning: Supervised Learning", "Linear & logistic regression, decision trees, random forests, support vector machines, and ensemble methods.", 4, "Intermediate", 97, ["Machine Learning Engineer"], ["Predicting Customer Churn"], ["Scikit-Learn", "Machine Learning"]),
            ("DS301", "Unsupervised Learning & NLP", "Clustering (K-means, Hierarchical), Principal Component Analysis (PCA), text tokenization, sentiment analysis, and vector embeddings.", 4, "Intermediate", 95, ["NLP Specialist"], ["Customer Segmentation Tool"], ["NLP", "Clustering"]),
            ("DS302", "Big Data Engineering", "Data pipelines using Apache Spark, Hadoop, SQL databases, ETL flows, and running analytics on distributed clusters.", 4, "Advanced", 96, ["Data Engineer"], ["Log Analytics Pipeline with Spark"], ["Spark", "ETL"]),
            ("DS401", "Deep Learning & AI Systems", "Multi-layer perceptrons, Convolutional Neural Networks (CNNs) for vision, and Recurrent Neural Networks (RNNs) for sequential data.", 4, "Advanced", 98, ["Computer Vision Engineer"], ["Digit Recognizer with PyTorch"], ["Deep Learning", "PyTorch"]),
            ("DS402", "Data Ethics & Privacy", "Understanding GDPR, ethical biases in algorithms, data anonymization techniques, and transparency in predictive modeling.", 3, "Advanced", 89, ["Compliance Officer"], ["Audit Report of Bias in Hiring AI"], ["Ethics", "Bias Auditing"])
        ]
    else:
        topic_pool = [
            ("GEN101", "Introduction to Digital Systems", "Introduction to computers, digital ecosystems, search strategies, and spreadsheets.", 3, "Beginner", 80, ["Office Coordinator"], ["Personal Budget Tracker"], ["Excel", "Digital Literacy"]),
            ("GEN102", "Critical Thinking & Design", "Problem statement definitions, ideation, wireframing, and user-centric design theories.", 3, "Beginner", 82, ["Product Assistant"], ["Customer Journey Map"], ["Design Thinking", "UX"]),
            ("GEN201", "Project Management Principles", "Introduction to Agile, Scrum, gantt charts, stakeholder communications, and scope control.", 4, "Intermediate", 85, ["Project Manager"], ["Sprint Schedule Plan"], ["Agile", "Scrum"]),
            ("GEN202", "Digital Marketing Foundations", "SEO optimizations, Google Analytics, content curation, social media outreach, and landing page conversions.", 3, "Intermediate", 88, ["SEO Optimizer"], ["Personal Blog Brand Launch"], ["SEO", "Copywriting"]),
            ("GEN301", "Business Analytics", "Interpreting charts, forecasting sales, building business models, and pivot tables.", 4, "Intermediate", 90, ["Business Analyst"], ["Quarterly Performance Report"], ["Analytics", "Excel"]),
            ("GEN302", "Innovation & Entrepreneurship", "Creating startup pitch decks, funding structures, business model canvas, and minimum viable products.", 4, "Advanced", 92, ["Startup Founder"], ["Business Pitch Presentation"], ["Business Model", "Strategy"]),
            ("GEN401", "Global Leadership & Ethics", "Leading multicultural teams, corporate social responsibility, and ethical frameworks in corporate spaces.", 4, "Advanced", 87, ["Team Lead"], ["Case Study on Corporate Crisis"], ["Leadership", "Ethics"]),
            ("GEN402", "Capstone Project Launch", "Putting together all concepts to launch a functional prototype or write an extensive research thesis paper.", 4, "Advanced", 95, ["Product Manager"], ["Launchable Web Prototype"], ["Product Design", "Testing"])
        ]

    semesters = []
    course_index = 0
    
    for sem in range(1, duration + 1):
        semester_courses = []
        num_courses = 2 if duration >= 6 else 3
        for _ in range(num_courses):
            orig_course = topic_pool[course_index % len(topic_pool)]
            prereqs = []
            if sem > 1:
                prev_sem_c = semesters[sem - 2]['courses'][0]['code']
                prereqs.append(prev_sem_c)
                
            course_data = {
                "code": f"{orig_course[0]}-S{sem}",
                "name": orig_course[1],
                "description": orig_course[2],
                "credits": orig_course[3],
                "learning_outcomes": [
                    f"Master the core principles of {orig_course[1]}.",
                    f"Successfully complete the hands-on project: {orig_course[6][0]}.",
                    f"Demonstrate fluency in using: {', '.join(orig_course[8])}."
                ],
                "prerequisites": prereqs,
                "assessment_methods": [
                    "Individual Practical Assignments: 40%",
                    "Mid-term Conceptual Test: 30%",
                    "Final Project Submission: 30%"
                ],
                "difficulty": orig_course[4],
                "learning_time_weeks": 15,
                "weekly_hours": orig_course[3] * 2,
                "industry_relevance_score": orig_course[5] + random.randint(-5, 2),
                "career_opportunities": orig_course[6],
                "recommended_projects": orig_course[7],
                "key_skills": orig_course[8],
                "resources": [
                    {"title": f"ACM/IEEE Guidelines on {orig_course[1]}", "url": f"https://www.acm.org/search?q={orig_course[1].replace(' ', '+')}"},
                    {"title": f"IBM Cognitive Class: {orig_course[8][0] if orig_course[8] else 'Introduction'}", "url": f"https://cognitiveclass.ai/courses?search={orig_course[8][0].replace(' ', '+') if orig_course[8] else 'IT'}"}
                ]
            }
            if course_data["industry_relevance_score"] > 100:
                course_data["industry_relevance_score"] = 100
                
            semester_courses.append(course_data)
            course_index += 1
            
        semesters.append({
            "semester_number": sem,
            "courses": semester_courses
        })
        
    return {
        "title": title,
        "field_of_study": field,
        "duration_semesters": duration,
        "semesters": semesters,
        "resource_sources": [
            "ACM/IEEE Joint Curriculum Guidelines (Mock Fallback)",
            "IBM Skills Network Course Frameworks (Mock Fallback)",
            "Hugging Face Applied NLP Curriculum (Mock Fallback)",
            "LERNIX Smart Heuristic Pipeline"
        ]
    }

def generate_mock_study_plan(course_name, weekly_hours):
    """Generates a detailed study plan for student assistant UI"""
    weekly_hours = int(weekly_hours)
    study_schedule = []
    
    topics = [
        "Foundations and Setup",
        "Intermediate Concepts and Architecture",
        "Practical Implementation & Coding Labs",
        "Project Optimization & Revision"
    ]
    
    # Map reference resource links for weeks
    resource_links = [
        [
            {"title": "MDN Core Language Guide", "url": f"https://developer.mozilla.org/en-US/search?q={course_name.replace(' ', '+')}"},
            {"title": "W3Schools Reference Documentation", "url": f"https://www.w3schools.com/search/index.php?q={course_name.replace(' ', '+')}"}
        ],
        [
            {"title": "IBM Cognitive Class", "url": f"https://cognitiveclass.ai/courses?search={course_name.replace(' ', '+')}"},
            {"title": "GeeksforGeeks Tutorial", "url": f"https://www.geeksforgeeks.org/search?q={course_name.replace(' ', '+')}"}
        ],
        [
            {"title": "Github Code Repository Examples", "url": f"https://github.com/search?q={course_name.replace(' ', '+')}"},
            {"title": "Hugging Face Models", "url": f"https://huggingface.co/models?search={course_name.replace(' ', '+')}"}
        ],
        [
            {"title": "LeetCode Practice Problems", "url": f"https://leetcode.com/problemset/all/?search={course_name.replace(' ', '+')}"},
            {"title": "StackOverflow Developer Forums", "url": f"https://stackoverflow.com/search?q={course_name.replace(' ', '+')}"}
        ]
    ]
    
    for i in range(1, 5):
        hours_distribution = [
            f"Read theoretical literature ({int(weekly_hours * 0.3)} hours)",
            f"Watch course lectures & demonstrations ({int(weekly_hours * 0.2)} hours)",
            f"Hands-on coding exercises/labs ({int(weekly_hours * 0.5)} hours)"
        ]
        
        study_schedule.append({
            "week": i,
            "topic": f"{topics[i-1]} of {course_name}",
            "tasks": hours_distribution,
            "resources": resource_links[i-1],
            "milestone": f"Complete Phase {i} self-assessment quiz & lab exercise."
        })
        
    revision_roadmap = [
        {
            "phase": "Phase 1: Foundation Building",
            "timeline": "Week 1",
            "focus": "Core jargon, environment initialization, basic constructs.",
            "checkpoints": ["Compile simple demo script", "Answer key theory questions"]
        },
        {
            "phase": "Phase 2: Deep Dive",
            "timeline": "Weeks 2-3",
            "focus": "Architectural patterns, logic implementations, API interactions.",
            "checkpoints": ["Integrate databases/modules", "Debug standard errors"]
        },
        {
            "phase": "Phase 3: Integration & Review",
            "timeline": "Week 4",
            "focus": "Optimization, security practices, Capstone build review.",
            "checkpoints": ["Run unit test suite", "Conduct mock interview prep"]
        }
    ]
    
    interview_prep = [
        {
            "topic": f"Core {course_name} Interview Concepts",
            "sample_questions": [
                {
                    "question": f"What are the primary design principles applied in {course_name}?",
                    "answer": f"The primary focus centers around efficiency, modular architecture, and industry compliance. This ensures codebases are scalable, reusable, and easy to maintain by distributed engineering teams."
                },
                {
                    "question": f"Explain how you would handle scale and error propagation in {course_name}.",
                    "answer": f"Scale is handled via horizontal replication and resource offloading. Error propagation is managed through structural error-handling blocks, fallback defaults, and comprehensive centralized logger alerts."
                }
            ]
        }
    ]
    
    return {
        "course_name": course_name,
        "weekly_hours_allocated": weekly_hours,
        "weekly_schedule": study_schedule,
        "revision_roadmap": revision_roadmap,
        "interview_preparation": interview_prep,
        "resource_sources": [
            "LeetCode Interview Guides (Mock Fallback)",
            "GeeksforGeeks Academic Prep Sheets (Mock Fallback)",
            "LERNIX Smart Heuristic Student Assistant"
        ]
    }
