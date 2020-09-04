# Book and movie recommender web site #
* Books and movies recommender site based on item contents and users in Django.
## Specifications: ##
* Books recommender is based on book title, author, genres and description.
* Movies recommender is based on book title, casts, genres, description and director.
* User based recommend is supported. Users have to rate at least 5 items to see their recommendations.
* Supports user registration, login and logout.
* Supports adding new books or movies. 
* Users can rate books or movies which are not rated by user.
* At home page popular books and movies are listed using True Bayesian Estimate formula.
* Books and movies search is supported.
* Users profile page is listed users rated books and movies and their recommended books and movies based on other users.
* There is another book database system on the site (_old_books/_). This also supports comment system.
## Dependencies: ##
* Pandas
* NumPy
* Django
* mysqlclient
* MySQL
* scikit-learn
* scikit-surprise
* Bootstrap 4
* django-crispy-forms
* (requirements texts are verbose)
## Run: ##
* First you should do MySQL configurations. Once you download the repository run following commands on the same directory with `manage.py`: 
`python manage.py makemigrations` and `python manage.py migrate` then create sql scripts for given 4 cvs files and users by using code piece from Jupyter Notebook. 
Run sql script. Copy your favorite image to _rcsystem/static/rcsystem/images/_. When it is finished run `python manage.py runserver` and go to http://127.0.0.1:8000/.
Create a new user for you, rate at least 5 books and 5 movies then get your recommended books and movies!
## Datasets: ##
* Book dataset:
  * I use datasets from Kaggle. In the Jupyter Notebook file (it is a little messy) you can see how the datasets are processed, merged and models are created. 
  Also all the links and licences is shown. Additionaly I crawled around 3000 books description, genres etc.
* Movie dataset:
  * Again, I use Kaggle datasets. A movie poster dataset and general movie dataset is merged.
## Images: ##
<table>
    <tr>
        <td align="center">
            <img src="https://github.com/perought/recommender-web-site/blob/master/test/home-page.jpg" alt="home-page" width="384" height="216">
            <br />
            <i> home page of the site </i>
        </td>
        <td align="center">
            <img src="https://github.com/perought/recommender-web-site/blob/master/test/profile.jpg" alt="profile" width="384" height="216">
            <br />
            <i> user profile </i>
        </td>
    </tr>
    <tr>
        <td align="center">
            <img src="https://github.com/perought/recommender-web-site/blob/master/test/recommender.jpg" alt="recommender" width="384" height="216">
            <br />
            <i> recommend books of this book </i>
        </td>
        <td align="center">
            <img src="https://github.com/perought/recommender-web-site/blob/master/test/search.jpg" alt="serach" width="384" height="216">
            <br />
            <i> search movies </i>
        </td>
    </tr>
</table>

## TODO: ##
* Add generate sql script python file for book data and ratings, movie data and ratings, auth_user
### Bugs and Limitations: ###
* Only first 30 books or movies are fetching from database. When I fetch all of them, it is trying to send all items to site and this process slows down the system.
* To speed up and because of not matching user ratings dataset, I use first 671 users from the datasets.
* Due to limitation of physical memory, only first 10000 movies considered for content based recommendations.
* At home page, because of card views, show and less system not working properly.
* I am not sure if the user based recommender system is working properly.
* Except for popular books and movies order, recommend books and movies are not listing order of similarty score, instead, listings are according to order of their indices.
