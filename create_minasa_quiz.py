import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'minasaelearning.settings')
django.setup()

from sections.models import Quiz, Question, Answer
from django.contrib.auth.models import User

# Get the admin user
try:
    admin_user = User.objects.get(username='admin')
except User.DoesNotExist:
    print('Admin user not found')
    exit()

# Quiz data
quiz_data = {
    'title': 'Minasa Festival Knowledge Quiz',
    'description': 'Test your knowledge about the Minasa Festival, a colorful celebration held in Bustos, Bulacan, that honors the town\'s culture, history, and the famous "minasa" cookie! See how well you know the traditions, origins, and highlights of this vibrant event.',
    'questions': [
        {
            'text': 'The Minasa Festival is celebrated in which town of Bulacan?',
            'options': ['Malolos', 'Bustos', 'Baliuag', 'Plaridel'],
            'correct': 'B'
        },
        {
            'text': 'What product is mainly celebrated during the Minasa Festival?',
            'options': ['Pastillas', 'Minasa cookies', 'Chicharon', 'Ensaymada'],
            'correct': 'B'
        },
        {
            'text': 'The Minasa cookie is made primarily from what ingredient?',
            'options': ['Cassava', 'Rice flour', 'Arrowroot flour', 'Cornstarch'],
            'correct': 'C'
        },
        {
            'text': 'When is the Minasa Festival usually celebrated?',
            'options': ['January', 'February', 'March', 'April'],
            'correct': 'B'
        },
        {
            'text': 'The Minasa Festival coincides with the celebration of which event?',
            'options': ['Feast of San Isidro Labrador', 'Town Fiesta of Bustos', 'Independence Day', 'Holy Week'],
            'correct': 'B'
        },
        {
            'text': 'What does the word "minasa" mean in Filipino?',
            'options': ['To cook', 'To knead or mix dough', 'To bake', 'To shape'],
            'correct': 'B'
        },
        {
            'text': 'What is the main purpose of the Minasa Festival?',
            'options': ['To promote local tourism and products', 'To celebrate national heroes', 'To honor rice farmers', 'To showcase modern technology'],
            'correct': 'A'
        },
        {
            'text': 'Which of the following activities is commonly seen during the Minasa Festival?',
            'options': ['Street dancing', 'Boat racing', 'Lantern parade', 'Flower offering'],
            'correct': 'A'
        },
        {
            'text': 'What shape is the traditional minasa cookie often molded into?',
            'options': ['Heart', 'Fish', 'Diamond', 'Flower'],
            'correct': 'D'
        },
        {
            'text': 'Which saint is honored alongside the Minasa Festival celebration?',
            'options': ['St. Michael the Archangel', 'Sto. Niño', 'St. John the Baptist', 'St. Isidore the Farmer'],
            'correct': 'B'
        },
        {
            'text': 'The Minasa Festival highlights Bustos\' identity as a town known for its ______.',
            'options': ['Heritage houses', 'Agricultural produce', 'Pastries and delicacies', 'Music and art'],
            'correct': 'C'
        },
        {
            'text': 'Which group usually participates in the Minasa Festival street dancing competition?',
            'options': ['Senior citizens', 'Farmers', 'Students and youth groups', 'Local government employees only'],
            'correct': 'C'
        },
        {
            'text': 'What is the texture of a traditional minasa cookie?',
            'options': ['Chewy', 'Soft and moist', 'Crunchy and crisp', 'Sticky and dense'],
            'correct': 'C'
        },
        {
            'text': 'What color theme is often seen during Minasa Festival decorations?',
            'options': ['Yellow and green', 'Brown and white', 'Blue and gold', 'Red and black'],
            'correct': 'B'
        },
        {
            'text': 'The Minasa Festival showcases which aspect of Bustos\' heritage?',
            'options': ['Religious devotion and faith', 'Baking tradition and craftsmanship', 'Military history', 'Fishing industry'],
            'correct': 'B'
        },
        {
            'text': 'Which of the following best describes the Minasa cookie\'s flavor?',
            'options': ['Sweet and buttery', 'Salty and spicy', 'Bitter and tangy', 'Sour and fruity'],
            'correct': 'A'
        },
        {
            'text': 'The Minasa Festival serves as a symbol of ______ among Bustoseños.',
            'options': ['Unity and pride', 'Wealth and power', 'Modern innovation', 'Political influence'],
            'correct': 'A'
        },
        {
            'text': 'What traditional baking method was used to make minasa cookies in the past?',
            'options': ['Oven toaster', 'Clay oven (pugon)', 'Electric oven', 'Gas stove'],
            'correct': 'B'
        },
        {
            'text': 'Aside from minasa cookies, which other delicacy is also famous in Bustos?',
            'options': ['Pastillas de leche', 'Puto seko', 'Inipit', 'Tamales'],
            'correct': 'B'
        },
        {
            'text': 'The Minasa Festival helps preserve the cultural identity of Bustos through ______.',
            'options': ['Folk dances, food, and unity', 'Political campaigns', 'Business expos', 'Industrial development'],
            'correct': 'A'
        }
    ]
}

# Create the quiz
quiz = Quiz.objects.create(
    title=quiz_data['title'],
    description=quiz_data['description'],
    created_by=admin_user
)

print(f'Created quiz: {quiz.title}')

# Create questions and answers
for i, q_data in enumerate(quiz_data['questions'], 1):
    question = Question.objects.create(
        quiz=quiz,
        text=q_data['text'],
        order=i
    )

    # Create answers
    for j, option_text in enumerate(q_data['options']):
        option_letter = chr(65 + j)  # A, B, C, D
        is_correct = (q_data['correct'] == option_letter)

        Answer.objects.create(
            question=question,
            text=option_text,
            is_correct=is_correct
        )

    print(f'Created question {i}: {q_data["text"][:50]}...')

print(f'\nQuiz creation completed!')
print(f'Quiz: {quiz.title}')
print(f'Questions: {quiz.questions.count()}')
print(f'Total answers: {Answer.objects.filter(question__quiz=quiz).count()}')
