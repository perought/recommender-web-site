# Book and movie recommender web site #
* Books and movies recommender site based on item contents and users in Django.
## Specifications: ##
* Books recommender is based on book title, author, genres and description.
* Movies recommender is based on book title, casts, genres, description and director.
* User based recommend is supported. Users have to rate at least 5 items to see their recommendations.
* Supports adding new books or movies. 
* Users can rate books or movies which are not rated by user.
* At home page popular books and movies are listing using True Bayesian Estimate formula.
* Books and movies search is supported.
* Users profile page is listing users rated books and movies and their recommendation books and movies based on other users.
## Dependencies: ##
* Pandas
* NumPy
* Django
* beautifulsoup4
* mysqlclient
* MySQL
* scikit-learn
* scikit-surprise
* Bootstrap 4
* django-crispy-forms
* (requirements texts are verbose)
## Run: ##
* First you should do MySQL configurations. Once you download the repository run `python manage.py makemigrations` and `python manage.py migrate` 
then create sql scripts for given 4 cvs files by using code piece from Jupyter Notebook. Run sql script. When it is finished run `python manage.py runserver` 
and go to http://127.0.0.1:8000/
## Datasets: ##
* Book dataset:
  * I use datasets from Kaggle. In the Jupyter Notebook file (it is a little messy) you can see how the datasets are processed, merged and models are created. 
  Also all the links and licences is shown. Additionaly I crawled around 3000 books description, genres etc.
* Movie dataset:
  * Again, I use Kaggle datasets. A movie poster dataset and general movie dataset is merged.
## Images: ##
* image_1
### Bugs and Limitations: ###
* For limitation of physical memory, only first 10000 movies considered for content based recommendations.
* At home page, because of card views, show and less system not working properly.
* I am not sure if the user based recommender system is working properly.
* Except for popular books and movies order, recommend books and movies are not listing order of similarty score, instead, listings are according to order of their indices.
