import streamlit as st
import numpy as np

categories = {
    'Viparyayah (विपर्यय)' : '''This term refers to wrong perception or misunderstanding. It denotes a state of error or ignorance where one misapprehends reality, often due to an inversion of the true understanding. In a more detailed context within Samkhya, it can relate to the various forms of ignorance that distort one's understanding of the self and the world''',
    'Aśakti (अशक्ति)' : '''Ashakti translates to incapacity or inability. It signifies a state where one is unable to perform actions effectively due to various impairments, particularly regarding the sensory organs or cognitive functions. This incapacity can manifest in different forms, contributing to individuals' difficulties in discerning truths or fulfilling their potential''',
    'Tuṣṭi (तुष्टि)' : '''Tushti means contentment or satisfaction. It refers to a state of being pleased or content with one's circumstances or understanding. In Samkhya philosophy, it can signify a mental state that arises when the mind is at peace with reality, achieving a sense of well-being''',
    'Siddhi (सिद्धि)' : '''Siddhi denotes perfection or accomplishment. It implies the attainment of goals, mastery over certain skills, or realization of one's potential. In spiritual contexts, it can refer to the acquisition of supernatural powers or significant spiritual achievements. Siddhi is often discussed in relation to personal growth and the realization of one's true nature'''
 }
# Define questions and their corresponding scores
questions = {
    "Viparyayah (विपर्यय)": [
        # {"question": "How do you feel when a discussion doesn’t go your way?",
        #  "options": ["Very upset and defensive", "I would take it personally", 
        #              "I would think about their comments", "I would appreciate their feedback"]},
        # {"question": "Do you often worry about things you cannot change?",
        #  "options": ["Yes, constantly", "Sometimes", 
        #              "Rarely", "Not at all"]},
        # {"question": "How do you typically react to unexpected changes in plans?",
        #  "options": ["I panic and feel helpless", "I get annoyed but adjust", 
        #              "I try to find an alternative solution", "I accept it and adapt without issue"]},
        # {"question": "When you make a mistake, how do you handle it?",
        #  "options": ["I dwell on it and feel bad", "I blame others and feel victimized", 
        #              "I try to learn from it", "I move on quickly and assess what happened"]},
        # {"question": "How do you view challenges in your life?",
        #  "options": ["As burdensome and stressful", "As something to avoid", 
        #              "As opportunities to grow", "As essential for my development"]},
        # A-Vidya (Ignorance)
        {"question": "How often do you find yourself unsure about your true self or purpose in life?",
            "options": [
            ["Always; I feel very lost.", -3],
            ["Often; I have frequent doubts.", -2],
            ["Occasionally; I reflect on it but have some clarity.", -1],
            ["Rarely; I have a strong sense of self and purpose.", 0]
        ]},
        # "Asmita (Egoism)"
        {"question": "How do you react when someone challenges your abilities or opinions?",
            "options": [
            ["I feel extremely defensive and upset.", -3],
            ["I take it personally, but I try to manage.", -2],
            ["I consider it objectively but feel a bit uncomfortable.", -1],
            ["I appreciate the feedback and try to learn from it.", 0]
        ]},
        # "Raga (Attachment)" 
        {"question": "Do you often find it difficult to let go of things or people that bring you happiness?",
         "options": [
            ["Yes, I struggle significantly with attachment.", -3],
            ["Sometimes; I cling to certain things.", -2],
            ["I can let go, but I still have attachments.", -1],
            ["No, I manage to enjoy things without clinging to them.", 0]
        ]},
        # "Dvesa (Aversion)"
        {"question": "How often do you find yourself avoiding situations or people that cause you discomfort?",
         "options": [
            ["Always; I avoid them vigorously.", -3],
            ["Often; I tend to shy away from uncomfortable situations.", -2],
            ["Occasionally; I manage to face them sometimes.", -1],
            ["Rarely; I confront discomfort head-on.", 0]
        ]},
        # Abhinivesa (Clinging to Life)
        {"question": "How do you feel about the prospect of change or the unknown?",
         "options": [
            ["I fear it greatly and resist change.", -3],
            ["I feel anxious about it but try to adapt.", -2],
            ["I acknowledge uncertainty but welcome growth.", -1],
            ["I'm excited by the possibilities that change can bring.", 0]
        ]}                     
    ],

    "Aśakti (अशक्ति)": [
        {"question": "How often do you feel overwhelmed by responsibilities?",
         "options": [
             ["Very often", -3], 
             ["Sometimes", -2], 
            ["Rarely", -1], 
            ["Never", 0]
            ]},
        {"question": "Do you find it difficult to ask for help when needed?",
         "options": [
             ["Yes, all the time", -3], 
             ["Sometimes", -2], 
            ["I try to ask when I can", -1], 
            ["No, I ask freely", 0]]},
        {"question": "Do you feel anxious about social situations?",
         "options": [["Yes, constantly", -3], 
                     ["Occasionally", -2], 
                     ["Rarely", -1], 
                     ["Not at all", 0]]},
        {"question": "How do you respond to criticism?",
         "options": [["I get very defensive", -3], 
                     ["It hurts my feelings", -2], 
                     ["I consider it but feel okay", -1], 
                     ["I appreciate constructive criticism", 0]]},
        {"question": "Do you often feel you need approval from others?",
         "options": [["Yes, always", -3], 
                     ["Sometimes", -2], 
                     ["Hardly ever", -1], 
                     ["No, I trust myself", 0]]},
        {"question": "How often do you procrastinate on tasks?",
         "options": [["Very frequently", -3], 
                     ["Sometimes", -2], 
                     ["Rarely", -1], 
                     ["Almost never", 0]]},
        {"question": "Do changes in your routine make you anxious?",
         "options": [["Yes, a lot", -3], 
                     ["Somewhat", -2], 
                     ["A little", -1], 
                     ["Not at all", 0]]},
        {"question": "How do you feel when someone disagrees with you?",
         "options": [["I feel very uncomfortable", -3], 
                     ["I don't like it, but I cope", -2], 
                     ["I am fine with differing opinions", -1], 
                     ["I enjoy healthy debates", 0]]},
        {"question": "How often do you reflect on your feelings?",
         "options": [["Rarely", -3], 
                     ["Sometimes", -2], 
                     ["Often", -1], 
                     ["Always", 0]]},
        {"question": "How comfortable are you with new experiences?",
         "options": [["Very uncomfortable", -3], 
                     ["Somewhat", -2], 
                     ["Comfortable", -1], 
                     ["Very comfortable", 0]
                     ]},
        {"question": "Do you find it hard to let go of past mistakes?",
         "options": [["Yes, very hard", -3], 
                     ["Sometimes", -2], 
                     ["I try not to dwell on them", -1], 
                     ["No, I learn and move on", 0]
                     ]},
        {"question": "When faced with something challenging, what’s your first instinct?",
         "options": [["To avoid it", -3], 
                     ["To feel anxious and hesitate", -2], 
                     ["To tackle it head-on", -1], 
                     ["To seek help or advice", 0]
                     ]},
        {"question": "How often do you compare yourself to others?",
         "options": [["All the time", -3], 
                     ["Sometimes", -2], 
                     ["Rarely", -1], 
                     ["Never", 0]]
                     },
        {"question": "Do you find it difficult to express your thoughts?",
         "options": [["Yes, very difficult", -3], 
                     ["Somewhat difficult", -2], 
                     ["I manage to express myself", -1], 
                     ["I express myself freely", 0]
                     ]},
        {"question": "When you experience failure, how do you feel?",
         "options": [["Completely defeated", -3], 
                     ["Upset but recovering", -2], 
                     ["Disappointed but hopeful", -1], 
                     ["Motivated to try again", 0]
                     ]},
        {"question": "Do you feel pressure to conform to social norms?",
         "options": [["Yes, a lot", -3], 
                     ["Sometimes", -2], 
                     ["Hardly ever", -1], 
                     ["Not at all", 0]
                     ]},
        {"question": "How do you feel about your personal achievements?",
         "options": [["I don’t feel good enough", -3], 
                     ["I feel okay but want more", -2], 
                     ["I’m proud of my efforts", -1], 
                     ["I'm very proud and confident", 0]
                      ]},
        {"question": "Do you often feel guilty about things?",
         "options": [["Yes, often", -3], 
                     ["Sometimes", -2], 
                     ["Rarely", -1], 
                     ["Not at all", 0]
                     ]},
        {"question": "Are you generally optimistic about the future?",
         "options": [["Not at all", -3], 
                     ["Sometimes", -2], 
                     ["Usually", -1], 
                     ["Very optimistic", 0]
                     ]},
        {"question": "How often do you feel misunderstood by others?",
         "options": [["Very often", -3], 
                      ["Sometimes", -2], 
                     ["Rarely", -1], 
                      ["Never", 0]]},
        {"question": "Would you say you are adaptable to life's changes?",
         "options": [["Not at all", -3], 
                      ["Sometimes", -2], 
                     ["Usually", -1], 
                      ["Very adaptable", 0]]},
        {"question": "Do you feel that you have control over your life choices?",
         "options": [["Not at all", -3], 
                      ["Sometimes", -2], 
                     ["Most of the time", -1], 
                      ["Completely", 0]]},
        {"question": "How do you react when you’re challenged?",
         "options": [["I feel overwhelmed", -3], 
                      ["I get frustrated", -2], 
                     ["I try my best", -1], 
                      ["I view it as an opportunity", 0]]},
        {"question": "How much do you value your opinions?",
         "options": [["Not at all", -3], 
                      ["A little", -2], 
                     ["Moderately", -1], 
                      ["Very much", 0]]},
        {"question": "Are you comfortable making decisions on your own?",
         "options": [["Not comfortable at all", -3], 
                      ["Somewhat uncomfortable", -2], 
                     ["Comfortable", -1], 
                      ["Very comfortable", 0]]},
        {"question": "How often do you feel bored with your routine?",
         "options": [["Very often", -3], 
                      ["Sometimes", -2], 
                     ["Rarely", -1], 
                     ["Never", 0]]},
        {"question": "Do you feel that your thoughts are often chaotic?",
         "options": [["Yes, very chaotic", -3], 
                      ["Sometimes", -2], 
                     ["Rarely", -1], 
                      ["No, they're generally clear", 0]]},
        {"question": "How often do you reflect on your values and beliefs?",
         "options": [["Rarely", -3], 
                      ["Sometimes", -2], 
                     ["Often", -1], ["Always", 0]]}
    ],
    "Tuṣṭi (तुष्टि)": [
        {"question": "What makes you feel truly happy?",
         "options": [["Receiving praise from others",  -3],
                      ["Buying new things",  -2],
                     ["Spending time with friends and family",  -1],
                      ["Achieving personal goals", 0]
                      ]},
        {"question": "How satisfied are you with your life right now?",
         "options": [["Very unsatisfied",  -3],
                      ["Somewhat unsatisfied",  -2],
                     ["Generally satisfied",  -1],
                      ["Very satisfied", 0]
                      ]},
        {"question": "Do you find joy in simple things?",
         "options": [["Not really",  -3],
                      ["Sometimes",  -2],
                     ["Often",  -1],
                      ["Always",  0]
                      ]},
        {"question": "How do you feel about helping others?",
         "options": [["It feels like a chore",  -3], 
                      ["I do it when I have to",  -2], 
                     ["I enjoy it",  -1], 
                      ["It makes me really happy",  0]
                      ]},
        {"question": "Do you often reflect on what makes you truly content?",
         "options": [["Not ever",  -3], 
                      ["Rarely",  -2], 
                     ["Sometimes",  -1], 
                      ["Yes, often",  0]
                      ]},
        {"question": "Do you celebrate small achievements?",
         "options": [["Hardly ever",  -3], 
                      ["Sometimes",  -2], 
                     ["Often",  -1], 
                     ["Always",  0]
                     ]},
        {"question": "How do you feel about your daily routine?",
         "options": [["I find it dull",  -3], 
                      ["It’s okay",  -2], 
                     ["I enjoy most of it",  -1], 
                     ["I love it",  0]
                     ]},
        {"question": "When facing challenges, do you feel you can manage stress?",
         "options": [["Not at all",  -3], 
                      ["Somewhat",  -2], 
                     ["Usually",  -1], 
                      ["Very well",  0]
                      ]},
        {"question": "Do you appreciate the moments of solitude?",
         "options": [["No, I dislike it",  -3], 
                      ["Sometimes",  -2], 
                     ["I don’t mind it",  -1], 
                      ["Yes, I cherish them",  0]
                      ]}
    ],
    "Siddhi (सिद्धि)": [
        {"question": "How comfortable are you in making conclusions based on limited information?",
         "options": [["Very uncomfortable; I doubt my judgments.", -2], 
                     ["Somewhat uncomfortable; I hesitate.", -1], 
                     ["I can make reasonable conclusions.", 1], 
                     ["I feel confident and rarely have doubts.", 2]]},
        {"question": "How often do you engage in study or reading to enhance your knowledge?",
         "options": [["Rarely or never.", -2], 
                     ["Occasionally when I feel like it.", -1], 
                     ["Often; I enjoy learning new things.", 1], 
                     ["Daily; it’s a significant part of my routine.", 2]]},
        {"question": "When facing difficulties, how do you usually cope?",
         "options": [["I struggle and feel overwhelmed.", -2], 
                     ["I try, but it takes a long time to recover.", -1], 
                     ["I manage to bounce back after some time.", 1], 
                     ["I quickly find solutions and move forward.", 2]]},
        {"question": "How do you handle relationships with others?",
         "options": [["I find it challenging to connect with people.", -2], 
                     ["I have some close friends but struggle with new relationships.", -1], 
                     ["I maintain good friendships and enjoy socializing.", 1], 
                     ["I have a wide circle of friends and mentors.", 2]]},
        {"question": "How frequently do you engage in acts of generosity or kindness?",
         "options": [["Rarely; I focus on my own needs.", -2], 
                     ["Sometimes; I give when it’s convenient.", -1], 
                     ["Often; I enjoy helping others when I can.", 1], 
                     ["Always; it’s important to me to help others regularly.", 2]]},
        {"question": "How confident are you in your abilities or talents?",
         "options": [["I have no special talents.", -2], 
                     ["I have a few but am not very confident.", -1], 
                     ["I have developed some talents and skills.", 1], 
                     ["I have multiple strong talents I cultivate actively.", 2]]},
        {"question": "How well do you understand your own emotions and those of others?",
         "options": [["I struggle to identify my feelings and others’ feelings.", -2], 
                     ["I can recognize some emotions.", -1], 
                     ["I understand emotions fairly well.", 1], 
                     ["I am very attuned to emotions, both mine and others’.", 2]]},
        {"question": "How effective are you in impacting or influencing others positively?",
         "options": [["I find it hard to influence anyone.", -2], 
                     ["I can persuade occasionally but not always.", -1], 
                     ["I influence those around me effectively.", 1], 
                     ["I am a natural leader and inspire many.", 2]]}
    ]
}

# Streamlit application
# st.title("Self-Assessment Questionnaire")

total_scores = {}

# Function to process each category of questions
def calc_scores(category, questions):
    score = 0
    total_scores[category] = 0
    st.markdown(f'{category} - {categories.get(category)}')
    for q in questions:
        qnp = np.array(q['options'])        
        selected_option = st.radio(q["question"], qnp[:, 0], key=q["question"])
        selected_option_score = int(qnp[qnp[:, 0] == selected_option, 1])
        total_scores[category] += selected_option_score   # Update the score based on selection

def process_questions():
    # Process each category of questions
    for category, qs in questions.items():
        calc_scores(category, qs)

def show_score():
    # Display total scores and calculate total clarity of thinking index
    st.subheader("Total Scores Summary:")
    clarity_of_thinking_index = sum(total_scores.values())
    for category, score in total_scores.items():
        st.write(f"{category} Score: {score}")

    # Display clarity of thinking index
    st.write(f"Your Clarity of Thinking Index: {clarity_of_thinking_index}")

    # Providing interpretation of the scores
    # if clarity_of_thinking_index < 0:
    #     st.write("You might want to work on your clarity of thinking.")
    # elif clarity_of_thinking_index == 0:
    #     st.write("You are at a neutral level. Consider focusing on personal growth.")
    # else:
    #     st.write("You have a good level of clarity of thinking and insight!")

# process_questions()
# show_score()        