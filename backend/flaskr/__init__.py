from crypt import methods
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
from models import Category

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)
    
    """
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    #   CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    
    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers 
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response
    
    # Route specific CORS access
    @app.route('/messages')
    @cross_origin()
    def get_messages():
        return 'GETTING MESSAGES'


    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        page = request.args.get('page', 1, type=int)
        start = (page -1) * 10
        end = start + 10
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        return jsonify({'success': True,
                        'categories': formatted_categories[start:end],
                        'all_categories': len(formatted_categories)
                        })

    @app.route('/categories/<int:catgory_id>', methods=['GET', 'PATCH'])
    def category(catgory_id):
        category = Category.query.filter(Category.id == catgory_id).one_or_none()
        
        if category is None:
            abort(404)
        else:
            return jsonify({'success': True,
                        'data': category.format(),
                        })

        
    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    
    @app.route('/questions')
    def get_questions():
        try:
            all_questions = Question.query.order_by(Question.id).all()
            paginated_questions = paginate_questions(request, all_questions)

            # if the page number is not found
            if (len(paginated_questions) == 0):
                abort(404)

            # get all categories
            categories = Category.query.all()
            categoriesDict = {}
            for category in categories:
                categoriesDict[category.id] = category.type

            return jsonify({
                'success': True,
                'questions': paginate_questions,
                'total_questions': len(all_questions),
                'categories': categoriesDict
            })
        except Exception as e:
            print(e)
            abort(400)
        
        

    """ 
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
            
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter_by(id=question_id).one_or_none()
            # if the question is not found
            if question is None:
                abort(404)

            question.delete()
            
            current_questions = Question.query.order_by(Question.id).all()
            formatted_questions = [current_questions.format() for question in current_questions]
            
            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": formatted_questions,
                    "all_questions": len(formatted_questions),
                }
            )

        except Exception as e:
            print(e)
            abort(404)
    

    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        dificulty = body.get("dificulty", None)
        
        try:
            # add ..
            question = Question(question=question, answer=answer,
                                category=category, difficulty=dificulty)
            question.insert()

            current_questions = Question.query.order_by(Question.id).all()
            formatted_questions = [current_questions.format() for question in current_questions]

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': formatted_questions,
                'total_questions': len(current_questions)
            })

        except Exception as e:
            print(e)
            abort(422)
        

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    
    @app.route("/search", methods=['POST'])
    def search():
        body = request.get_json()
        search = body.get('searchTerm')
        all_questions = Question.query.filter(
            Question.question.ilike('%'+search+'%')).all()

        if all_questions:
            current_questions = paginate_questions(request, all_questions)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(all_questions)
            })
        else:
            abort(404)


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:id>/questions")
    def questions_in_category(id):
        category = Category.query.filter_by(id=id).one_or_none()
        if category:
            category_questions = Question.query.filter_by(category=str(id)).all()
            current_questions = paginate_questions(request, category_questions)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(category_questions),
                'current_category': category.type
            })
        else:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
            }), 404
        
    return app

