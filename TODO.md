# TODO: Add Quiz and Minigame Levels Counts to Admin Dashboard

## Tasks
- [x] Update `admin_dashboard` view in `sections/views.py` to include `total_quizzes` and `total_minigame_levels` in context
- [x] Update `admin-dashboard.html` template to add two new stat cards for quizzes and minigame levels
- [ ] Test the changes by running the server and checking the dashboard

## Notes
- Ensure the counts are accurate by querying Quiz and MinigameLevel models
- Style the new stat cards consistently with existing ones
- Add appropriate icons and colors for the new cards
