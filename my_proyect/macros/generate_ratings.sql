{% macro generate_ratings() %}
CASE
        WHEN user_rating >= 4.5 THEN 'Excellent'
        WHEN user_rating >= 3.5 THEN 'Good'
        WHEN user_rating >= 2.5 THEN 'Average'
        ELSE 'Poor'
    END AS rating_category

{% endmacro %}