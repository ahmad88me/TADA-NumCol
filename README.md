# TADA-NumCol

## parameters/configurations
### for the model
* min_num_of_objects = 30
* min_num of entities for a property = 30
### for the prediction
* percentage_of_num_per_col = 0.5 # at least how many of a numerical column has numerical values
* max_num_of_prediction_memberships = 10 (the number of top candidates which is also known as k)

## Further improvements
* Improve numerical scoring: If a column in the csv file is closer to a cluster C than all the other columns in that table, than probably other columns in that table belongs to another cluster
. Thus, other columns in that table must not be allowed to belong to that cluster (C).
