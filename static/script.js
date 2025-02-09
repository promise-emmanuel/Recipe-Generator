async function generateRecipe() {
    // Hide the saved recipes section
    document.getElementById("recipes-container").style.display = "none";

    // Show the generated recipe section
    document.getElementById("generated-recipe").style.display = "block";


    const ingredients = document.getElementById("ingredients").value;
    if (!ingredients) {
        alert("Please enter ingredients.");
        return;
    }
    
    const response = await fetch("/generate-recipe/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ingredients })
    });
    
    if (!response.ok) {
        alert("Error generating recipe.");
        return;
    }
    

    const recipeText = await response.text();

    // convert the plain text into html format
    document.getElementById("generated-recipe").innerHTML = recipeText;
}

async function saveRecipe() {
    const recipeText = document.getElementById("generated-recipe").innerText;
    if (!recipeText) {
        alert("No recipe to save.");
        return;
    }
    
    const response = await fetch("/save-recipe/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ recipe: recipeText })
    });
    
    if (!response.ok) {
        alert("Error saving recipe.");
        return;
    }
    
    alert("Recipe saved successfully!");
}


async function viewRecipes() {
    // Hide the generated recipe section
    document.getElementById("generated-recipe").style.display = "none";

    // Show the saved recipes section
    document.getElementById("recipes-container").style.display = "block";


    try {
        const response = await fetch("/view-recipes/");
        if (!response.ok) throw new Error("Failed to fetch recipes");

        const recipes = await response.json();
        const container = document.getElementById("recipes-container");
        container.innerHTML = "";

        recipes.forEach(recipe => {
            const recipeCard = document.createElement("div");
            recipeCard.className = "recipe-card";
            recipeCard.id = `recipe-${recipe.id}`;

            recipeCard.innerHTML = `
                <h2>Recipe #${recipe.id}</h2>
                <p>${recipe.recipe}</p>
                <button onclick="editRecipe(${recipe.id}, ${recipe.recipe})">Edit Recipe</button>
                <button onclick="deleteRecipe(${recipe.id})">Delete Recipe</button>
            `;

            container.appendChild(recipeCard);
        });
    } catch (error) {
        console.error("Error fetching recipes:", error);
    }
}


function editRecipe(recipeId, currentData) {
    // Create an editable text area
    const newRecipeText = prompt("Edit your recipe:", currentData);

    if (newRecipeText !== null) {
        fetch(`/edit-recipe/${recipeId}/`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ recipe_data: newRecipeText })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            viewRecipes(); // Refresh recipes list
        })
        .catch(error => console.error("Error editing recipe:", error));
    }
}



async function deleteRecipe(recipeId) {
    if (!confirm("Are you sure you want to delete this recipe?")) return;

    try {
        const response = await fetch(`/delete-recipe/${recipeId}/`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" }
        });

        if (!response.ok) {
            throw new Error("Failed to delete recipe");
        }

        // Remove the recipe from the UI
        document.getElementById(`recipe-${recipeId}`).remove();
        alert("Recipe deleted successfully!");
    } catch (error) {
        console.error("Error deleting recipe:", error);
        alert("Error deleting recipe.");
    }
}

