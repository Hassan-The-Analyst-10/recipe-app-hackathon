document.addEventListener('DOMContentLoaded', function() {
    const ingredientInput = document.getElementById('ingredient-input');
    const addIngredientBtn = document.getElementById('add-ingredient');
    const ingredientsList = document.getElementById('ingredients-list');
    const getRecipesBtn = document.getElementById('get-recipes');
    const clearAllBtn = document.getElementById('clear-all');
    const viewHistoryBtn = document.getElementById('view-history');
    const recipesContainer = document.getElementById('recipes-container');
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Recipe History</h2>
                <button class="close-modal">&times;</button>
            </div>
            <div class="history-list" id="history-list"></div>
        </div>
    `;
    document.body.appendChild(modal);
    
    let ingredients = [];
    
    // Add ingredient function
    function addIngredient() {
        const ingredient = ingredientInput.value.trim();
        if (ingredient && !ingredients.includes(ingredient)) {
            ingredients.push(ingredient);
            renderIngredients();
            ingredientInput.value = '';
            ingredientInput.focus();
        }
    }
    
    // Render ingredients list
    function renderIngredients() {
        ingredientsList.innerHTML = '';
        ingredients.forEach(ingredient => {
            const tag = document.createElement('div');
            tag.className = 'ingredient-tag';
            tag.innerHTML = `
                ${ingredient}
                <span class="remove-btn" data-ingredient="${ingredient}">×</span>
            `;
            ingredientsList.appendChild(tag);
        });
        
        // Add event listeners to remove buttons
        document.querySelectorAll('.remove-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const ingredientToRemove = this.getAttribute('data-ingredient');
                ingredients = ingredients.filter(i => i !== ingredientToRemove);
                renderIngredients();
            });
        });
    }
    
    // Clear all ingredients
    function clearAllIngredients() {
        ingredients = [];
        renderIngredients();
    }
    
    // Get recipes from backend
    function getRecipes() {
        if (ingredients.length === 0) {
            alert('Please add at least one ingredient');
            return;
        }
        
        // Show loading state
        recipesContainer.innerHTML = `
            <div class="recipe-card">
                <div class="recipe-image">
                    <i class="fas fa-spinner fa-spin"></i>
                </div>
                <div class="recipe-content">
                    <h3>Finding recipes...</h3>
                    <p>Our AI is analyzing your ingredients and finding the best recipes for you.</p>
                    <div class="recipe-meta">
                        <span>Please wait</span>
                        <span class="tech-badge">AI Processing</span>
                    </div>
                </div>
            </div>
        `;
        
        // Send request to backend
        fetch('/get_recipes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ingredients: ingredients })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            displayRecipes(data.recipes);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to get recipes. Please try again later.');
        });
    }
    
    // Display recipes in the UI
    function displayRecipes(recipes) {
        recipesContainer.innerHTML = '';
        
        if (recipes.length === 0) {
            recipesContainer.innerHTML = `
                <div class="recipe-card">
                    <div class="recipe-image">
                        <i class="fas fa-exclamation-circle"></i>
                    </div>
                    <div class="recipe-content">
                        <h3>No recipes found</h3>
                        <p>We couldn't find any recipes with those ingredients. Try adding more ingredients.</p>
                        <div class="recipe-meta">
                            <span>Try again</span>
                            <span class="tech-badge">No results</span>
                        </div>
                    </div>
                </div>
            `;
            return;
        }
        
        recipes.forEach(recipe => {
            const recipeCard = document.createElement('div');
            recipeCard.className = 'recipe-card';
            
            recipeCard.innerHTML = `
                <div class="recipe-image">
                    <i class="fas fa-utensils"></i>
                </div>
                <div class="recipe-content">
                    <h3>${recipe.name}</h3>
                    <p>${recipe.description}</p>
                    <div class="recipe-meta">
                        <span>Ready in: ${recipe.prep_time}</span>
                        <span class="tech-badge">${recipe.difficulty}</span>
                    </div>
                </div>
            `;
            
            recipesContainer.appendChild(recipeCard);
        });
    }
    
    // View recipe history
    function viewRecipeHistory() {
        fetch('/recipe_history')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }
                
                const historyList = document.getElementById('history-list');
                historyList.innerHTML = '';
                
                if (data.recipes.length === 0) {
                    historyList.innerHTML = '<p>No recipe history found.</p>';
                } else {
                    data.recipes.forEach(recipe => {
                        const historyItem = document.createElement('div');
                        historyItem.className = 'history-item';
                        
                        const date = new Date(recipe.created_at);
                        const formattedDate = date.toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric'
                        });
                        
                        historyItem.innerHTML = `
                            <h3>${recipe.name}</h3>
                            <p>${recipe.description}</p>
                            <div class="history-meta">
                                <span>${recipe.prep_time} • ${recipe.difficulty}</span>
                                <span>${formattedDate}</span>
                            </div>
                        `;
                        
                        historyList.appendChild(historyItem);
                    });
                }
                
                modal.style.display = 'flex';
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to load recipe history.');
            });
    }
    
    // Close modal
    function closeModal() {
        modal.style.display = 'none';
    }
    
    // Event listeners
    addIngredientBtn.addEventListener('click', addIngredient);
    
    ingredientInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addIngredient();
        }
    });
    
    getRecipesBtn.addEventListener('click', getRecipes);
    
    clearAllBtn.addEventListener('click', clearAllIngredients);
    
    viewHistoryBtn.addEventListener('click', viewRecipeHistory);
    
    document.querySelector('.close-modal').addEventListener('click', closeModal);
    
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });
});