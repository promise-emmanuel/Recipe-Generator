from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import sqlite3
from typing import List, Optional

from openai import OpenAI
import os, dotenv

dotenv.load_dotenv()
MODEL = os.environ["MODEL"]
client = OpenAI()

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

class RecipeRequest(BaseModel):
    ingredients: list[str]  # Ingredients as a list


# pydantic model to validate request data
class Add_Recipe(BaseModel):
    recipe_name: str
    ingredients: str
    instructions: Optional[str] = None
    
class GetRecipes(BaseModel):
    recipe_id: int
    recipe_name: str
    ingredients: str
    instructions: str  
    
class RecipeRequest(BaseModel):
    ingredients: str
    
class RecipeSaveRequest(BaseModel):
    recipe: str  # Recipe as a structured string
    
def insert_recipe(recipe_name, ingredients, instructions):
    conn = sqlite3.connect('recipe.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO recipes (recipe_name, ingredients, instructions) VALUES (?, ?, ?)",
        (recipe_name, ingredients, instructions)
    )
    
    conn.commit()
    conn.close()


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
    


def get_db_connection():
    conn = sqlite3.connect("recipes.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.post("/generate-recipe/")
async def generate_recipe(request: RecipeRequest):
    prompt = f"""
    Create a unique recipe using the following ingredients: {(request.ingredients)}.
    Provide your response wrapped in a format that will work on this code = const recipeText = await response.text();

    // convert the plain text into html format
    document.getElementById("generated-recipe").innerHTML = recipeText; :
    
    <h4>Recipe Name</h4>
    <p>Ingredients</p>
    <p>Step-by-step Instructions<p>
    
    For example:
    <h4>Refreshing Cucumber and Tomato Salad</h4>
    <p>Ingredients: Cucumber, tomatoes</p>
    <p>Instructions: Cucumber, tomatoes</p>
    
    Make sure the instructions is brief as possible.
    """

    messages = [
        {"role": "system", "content": "You are a professional chef generating structured recipes."},
        {"role": "user", "content": prompt}
    ]

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )

        recipe_text = completion.choices[0].message.content

        # the response is plain text
        return recipe_text

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recipe: {str(e)}")

@app.post("/save-recipe/")
async def save_recipe(request: Request):
    try:
        data = await request.json()
        recipe_text = data.get("recipe", "").strip()

        if not recipe_text:
            raise HTTPException(status_code=400, detail="Recipe text is empty")

        conn = sqlite3.connect("recipes.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO recipes (recipe_data) VALUES (?)", (recipe_text,))
        conn.commit()
        conn.close()

        return JSONResponse(content={"message": "Recipe saved successfully!"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving recipe: {str(e)}")


@app.get("/view-recipes/")
async def view_recipes():
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, recipe_data FROM recipes")
    recipes = [{"id": row[0], "recipe": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    return JSONResponse(content=recipes)


@app.put("/edit-recipe/{recipe_id}/")
async def edit_recipe(recipe_id: int, request: dict):
    new_recipe_data = request.get("recipe_data")
    
    if not new_recipe_data:
        raise HTTPException(status_code=400, detail="Invalid recipe data")

    conn = sqlite3.connect("recipes.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE recipes SET recipe_data = ? WHERE id = ?", (new_recipe_data, recipe_id))
    conn.commit()
    conn.close()

    return {"message": "Recipe updated successfully!"}




@app.delete("/delete-recipe/{recipe_id}/")
async def delete_recipe(recipe_id: int):
    try:
        conn = sqlite3.connect("recipes.db")
        cursor = conn.cursor()

        # Check if recipe exists
        cursor.execute("SELECT id FROM recipes WHERE id = ?", (recipe_id,))
        recipe = cursor.fetchone()
        if not recipe:
            conn.close()
            raise HTTPException(status_code=404, detail="Recipe not found")

        # Delete the recipe
        cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        conn.commit()
        conn.close()

        return {"message": "Recipe deleted successfully"}

    except Exception as e:
        return {"error": str(e)}



# Running the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)



    