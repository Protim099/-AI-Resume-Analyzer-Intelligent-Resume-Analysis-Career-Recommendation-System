"""Skill taxonomy, aliases, job-role profiles and learning suggestions."""

SKILL_CATEGORIES = {
    "Programming Languages": ["Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go", "Rust", "PHP",
                              "Ruby", "Kotlin", "Swift", "R", "MATLAB", "Scala", "Dart", "Bash", "SQL"],
    "Web Development": ["React", "Angular", "Vue.js", "Next.js", "Node.js", "Express.js", "HTML", "CSS",
                        "Tailwind CSS", "Bootstrap", "Redux", "jQuery", "REST API", "GraphQL", "Django", "Flask",
                        "FastAPI", "Spring Boot", "Laravel", ".NET", "WebSocket"],
    "Databases": ["PostgreSQL", "MySQL", "MongoDB", "SQLite", "Redis", "Oracle", "SQL Server", "Firebase",
                  "Elasticsearch", "Cassandra", "SQLAlchemy"],
    "Data Science & AI": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "TensorFlow", "PyTorch",
                          "Keras", "scikit-learn", "spaCy", "Pandas", "NumPy", "Matplotlib", "Seaborn", "OpenCV",
                          "Hugging Face", "Transformers", "LLM", "Data Analysis", "Data Visualization", "Power BI",
                          "Tableau", "Statistics", "Apache Spark", "Hadoop", "Data Mining", "Generative AI"],
    "Cloud & DevOps": ["Docker", "Kubernetes", "AWS", "Azure", "Google Cloud", "CI/CD", "Jenkins", "GitHub Actions",
                       "Terraform", "Ansible", "Linux", "Nginx", "Git", "GitHub", "GitLab", "Heroku", "Microservices"],
    "Tools & Practices": ["Agile", "Scrum", "JIRA", "Postman", "VS Code", "Excel", "Unit Testing", "Pytest", "Jest",
                          "Selenium", "Figma", "OOP", "Data Structures", "Algorithms", "System Design",
                          "Design Patterns"],
    "Mobile": ["Android", "iOS", "Flutter", "React Native"],
    "Soft Skills": ["Communication", "Teamwork", "Leadership", "Problem Solving", "Critical Thinking",
                    "Time Management", "Adaptability", "Creativity", "Collaboration", "Project Management",
                    "Presentation", "Analytical Skills", "Decision Making", "Mentoring"],
}

ALIASES = {
    "js": "JavaScript", "ts": "TypeScript", "reactjs": "React", "react.js": "React", "node": "Node.js",
    "nodejs": "Node.js", "vue": "Vue.js", "vuejs": "Vue.js", "nextjs": "Next.js", "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL", "k8s": "Kubernetes", "sklearn": "scikit-learn", "scikit learn": "scikit-learn",
    "tf": "TensorFlow", "ml": "Machine Learning", "natural language processing": "NLP", "gcp": "Google Cloud",
    "golang": "Go", "expressjs": "Express.js", "express": "Express.js", "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS", "rest apis": "REST API", "restful api": "REST API", "restful apis": "REST API",
    "restful": "REST API", "ci cd": "CI/CD", "cicd": "CI/CD", "object oriented programming": "OOP",
    "object-oriented programming": "OOP", "dsa": "Data Structures", "data structure": "Data Structures",
    "problem-solving": "Problem Solving", "team work": "Teamwork", "team player": "Teamwork", "mongo": "MongoDB",
    "c sharp": "C#", "dotnet": ".NET", "asp.net": ".NET", "mssql": "SQL Server", "ms excel": "Excel",
    "microsoft excel": "Excel", "powerbi": "Power BI", "huggingface": "Hugging Face", "pyspark": "Apache Spark",
    "spark": "Apache Spark", "large language models": "LLM", "llms": "LLM", "springboot": "Spring Boot",
    "spring": "Spring Boot", "microservice": "Microservices", "unit tests": "Unit Testing", "analytical": "Analytical Skills",
    "analytical thinking": "Analytical Skills", "communication skills": "Communication", "leadership skills": "Leadership",
    "computer vision": "Computer Vision", "opencv": "OpenCV", "algorithm": "Algorithms",
}

# Short / ambiguous names must match with exact case.
CASE_SENSITIVE = {"C", "R", "Go", "Swift", "Scala", "Ruby", "Rust", "Dart", "Oracle", "Express.js", "Spring Boot"}

ROLE_PROFILES = {
    "Full Stack Developer": {"core": ["JavaScript", "React", "Node.js", "HTML", "CSS", "SQL", "REST API", "Git"],
                             "nice": ["TypeScript", "Docker", "MongoDB", "PostgreSQL", "AWS"]},
    "Frontend Developer": {"core": ["JavaScript", "HTML", "CSS", "React", "Git"],
                           "nice": ["TypeScript", "Tailwind CSS", "Redux", "Next.js", "Figma", "Jest"]},
    "Backend Developer": {"core": ["Python", "SQL", "REST API", "PostgreSQL", "Git", "Docker"],
                          "nice": ["FastAPI", "Django", "Redis", "AWS", "Microservices", "Pytest"]},
    "Java Developer": {"core": ["Java", "Spring Boot", "SQL", "REST API", "OOP", "Git"],
                       "nice": ["MySQL", "Microservices", "Docker", "Unit Testing"]},
    "Data Scientist": {"core": ["Python", "Machine Learning", "Pandas", "NumPy", "scikit-learn", "Statistics", "SQL"],
                       "nice": ["Deep Learning", "Data Visualization", "Matplotlib", "TensorFlow", "PyTorch"]},
    "Machine Learning Engineer": {"core": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Git"],
                                  "nice": ["Docker", "AWS", "scikit-learn", "Pandas", "Kubernetes"]},
    "NLP Engineer": {"core": ["Python", "NLP", "spaCy", "Transformers", "Machine Learning"],
                     "nice": ["PyTorch", "Hugging Face", "LLM", "scikit-learn", "Deep Learning"]},
    "Data Analyst": {"core": ["SQL", "Python", "Excel", "Data Visualization", "Statistics"],
                     "nice": ["Pandas", "Power BI", "Tableau", "Data Analysis", "Matplotlib"]},
    "DevOps Engineer": {"core": ["Linux", "Docker", "Kubernetes", "CI/CD", "Git", "AWS"],
                        "nice": ["Terraform", "Ansible", "Jenkins", "Bash", "Nginx", "GitHub Actions"]},
    "Cloud Engineer": {"core": ["AWS", "Linux", "Docker", "Terraform", "Git"],
                       "nice": ["Azure", "Google Cloud", "Kubernetes", "CI/CD", "Python"]},
    "Mobile App Developer": {"core": ["Flutter", "Dart", "Android", "Git", "REST API"],
                             "nice": ["React Native", "Kotlin", "iOS", "Swift", "Firebase"]},
    "Software Engineer": {"core": ["Data Structures", "Algorithms", "OOP", "Git", "Python", "Java"],
                          "nice": ["System Design", "SQL", "Design Patterns", "Unit Testing", "Docker"]},
    "QA / Test Engineer": {"core": ["Selenium", "Unit Testing", "Postman", "Agile", "JIRA"],
                           "nice": ["Pytest", "Jest", "Python", "CI/CD", "SQL"]},
}

# What to learn next once a skill is known (adjacent technologies).
RELATED = {
    "Python": ["FastAPI", "Pandas", "Pytest"], "JavaScript": ["TypeScript", "React", "Node.js"],
    "React": ["Next.js", "Redux", "TypeScript"], "Node.js": ["Express.js", "MongoDB", "GraphQL"],
    "HTML": ["CSS", "Tailwind CSS"], "SQL": ["PostgreSQL", "Data Analysis"], "Java": ["Spring Boot", "Microservices"],
    "Machine Learning": ["Deep Learning", "scikit-learn", "Docker"], "Deep Learning": ["PyTorch", "TensorFlow"],
    "Docker": ["Kubernetes", "CI/CD"], "Git": ["GitHub Actions", "CI/CD"], "AWS": ["Terraform", "Kubernetes"],
    "Pandas": ["NumPy", "Data Visualization"], "NLP": ["Transformers", "Hugging Face", "LLM"],
    "Linux": ["Bash", "Nginx"], "MongoDB": ["Redis", "PostgreSQL"], "Flask": ["FastAPI", "Docker"],
    "Django": ["REST API", "PostgreSQL"], "Flutter": ["Firebase", "Dart"], "C++": ["Data Structures", "Algorithms"],
}

SKILL_TO_CATEGORY = {s: cat for cat, skills in SKILL_CATEGORIES.items() for s in skills}
SOFT_SKILLS = set(SKILL_CATEGORIES["Soft Skills"])
