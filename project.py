from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import studio_id

app = Flask(__name__)

engine = create_engine('sqlite:///collectioncatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def categoryStudio(category_id):
    category = session.query(Category).first()
    studio_item = session.query(StudioItem).filter_by(category_id=category.id)
    output = ''
    for i in items:
        output += i.name
        output += '</br>'
        output += i.studio_id
        output += '</br>'
        output += i.description
        output += '</br>'
        output += '</br>'

    return output


@app.route('/categories/<int:category_id>/')
def categoryStudio(studio_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(StudioItem).filter_by(category_id=category_id)
    output = ''
    for i in items:
        output += i.name
        output += '</br>'
        output += i.price
        output += '</br>'
        output += i.description
        output += '</br>'
        output += i.studio_id
        output += '</br>'

    return output


@app.route('/categories/<int:category_id>/new', methods=['GET', 'POST'])
def newStudioItem(category_id):

    if request.method == 'POST':
        newStudioItem = MenuItem(name=request.form['name'],
                                 description=request.form[
                           'description'], price=request.form['price'],
                           course=request.form['course'],
                           category_id=category_id)
        session.add(newStudioItem)
        session.commit()
        return redirect(url_for('restaurantMenu', category_id=category_id))
    else:
        return render_template('newstudioitem.html', category_id=category_id)


@app.route('/categories/<int:category_id>/<int:studio_id>/edit',
           methods=['GET', 'POST'])
def editStudioItem(category_id, menu_id):
    editedStudioItem = session.query(StudioItem).filter_by(id=studio_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedStudio.name = request.form['name']
        session.add(editedStudio)
        session.commit()
        return redirect(url_for('restaurantMenu', category_id=category_id))
    else:
        # USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU
        # SHOULD USE IN YOUR EDITSTUDIO TEMPLATE
        return render_template(
            'editmenuitem.html', category_id=category_id,
            studio_id=studio_id, studio=editedStudio)


@app.route('/category/<int:category_id>/<int:studio_id>/delete/')
def deleteStudio(category_id, studio_id):
    return "page to delete a new Studio item."

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
