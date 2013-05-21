
#include <stdlib.h>
#include <stdio.h>

unsigned long mymem_count_alloc = 0;
unsigned long mymem_count_free  = 0;

void *
mem_alloc (size_t size)
{
    void *p;

    p = malloc(size);
    if (p)
    {
        mymem_count_alloc++;
    }
    return (p);
}

void 
mem_free (void *p)
{
    if (p)
    {
        free(p);
        mymem_count_free++;
    }
}

void 
mem_check (void)
{
    printf("%ld/%ld\n", mymem_count_alloc, mymem_count_free);
    if (mymem_count_alloc != mymem_count_free)
    {
        printf("%s\n", "WARNING: NUM MALLOC() != NUM FREE()");
    }
}

// The elements held in Quadtree leaves
struct PointData
{
    double x; 
    double y;
    int i;    // index used to track linked data
};

struct Quadtree;
struct Quadtree
{
    double min_x, max_x;
    double min_y, max_y;
    struct PointData *elements;
    int num_elements;
    int is_node;
    int buckets;
    struct Quadtree *NW;
    struct Quadtree *SW;
    struct Quadtree *NE;
    struct Quadtree *SE;
};

struct StackNode;
struct StackNode
{
    struct Quadtree *data;
    struct StackNode *prev;
};

int 
in_bounds(struct Quadtree *qtree, struct PointData *point)
{
    return (qtree->min_x <= point->x && point->x <= qtree->max_x &&
            qtree->min_y <= point->y && point->y <= qtree->max_y);
}

struct Quadtree* 
choose_node(struct Quadtree *qtree, struct PointData *point)
{
    const double min_x = qtree->min_x;
    const double min_y = qtree->min_y;
    const double max_y = qtree->max_y;
    const double dx_rng = qtree->max_x - min_x;
    const double dy_rng = max_y - min_y;
    int west = min_x <= point->x && point->x <= min_x + dx_rng / 2;
    int north = min_y + dy_rng / 2 <= point->y && point->y <= max_y;
    if (west)
    {
        if (north) return qtree->NW;    // NW
        else return qtree->SW;    // SW
    } 
    else
    {
        if (north) return qtree->NE;    // NE
        else return qtree->SE;    // SE
    }
    return NULL;    // should never get here
}

void branch();
int insert(struct Quadtree *qtree, struct PointData *point)
{
    struct Quadtree *pointer = qtree;
    if (!in_bounds(pointer, point)) {
        return 1;
    }
    while (1)
    {
        if (pointer->num_elements == pointer->buckets) {
            branch(pointer);
        }
        if (pointer->is_node) {
            pointer = choose_node(pointer, point);
        }
        else
        {   
            pointer->elements[pointer->num_elements] = *point;
            pointer->num_elements += 1;
            return 0;
        }
    }
    return 1;
}

struct Quadtree* 
make_qtree(double min_x, double max_x, double min_y, double max_y, int buckets)
{
    struct Quadtree *qtree = mem_alloc(sizeof(struct Quadtree));
    qtree->min_x = min_x;
    qtree->max_x = max_x;
    qtree->min_y = min_y;
    qtree->max_y = max_y;
    qtree->is_node = 0;
    qtree->num_elements = 0;
    qtree->buckets = buckets;
    qtree->elements = mem_alloc(buckets * sizeof(struct PointData));
    return qtree;
}

void 
leaf_to_node(struct Quadtree *qtree)
{
    const double min_x = qtree->min_x;
    const double max_x = qtree->max_x;
    const double min_y = qtree->min_y;
    const double max_y = qtree->max_y;
    const double mid_x = min_x + (max_x - min_x) / 2.0;
    const double mid_y = min_y + (max_y - min_y) / 2.0;
    const int b = qtree->buckets + 1;
    //printf("%f,%f,%f,%f\n", min_x, max_x, min_y, max_y);
    qtree->NE = make_qtree(mid_x, max_x, mid_y, max_y, b);
    qtree->NW = make_qtree(min_x, mid_x, mid_y, max_y, b);
    qtree->SE = make_qtree(mid_x, max_x, min_y, mid_y, b);
    qtree->SW = make_qtree(min_x, mid_x, min_y, mid_y, b);
    qtree->is_node = 1;
}

void 
branch(struct Quadtree *qtree)
{
    leaf_to_node(qtree);
    int stop_iteration = qtree->num_elements;
    for (int i = 0; i != stop_iteration; i++)
    {
        struct PointData element = qtree->elements[i];
        struct Quadtree *target_child = choose_node(qtree, &element);
        target_child->elements[target_child->num_elements] = element;
        target_child->num_elements += 1;
    }
    qtree->num_elements = 0;      // 
    mem_free(qtree->elements);    // don't need to hold elements here anymore
}

struct ResultNode;
struct ResultNode
{
    double x;
    double y;
    int i;
    struct ResultNode *prev;
};

struct ResultNode* 
query_range(struct Quadtree *qtree, double min_x, 
            double max_x, double min_y, double max_y)
{
    struct ResultNode *result = mem_alloc(sizeof(*result));
    result->prev = NULL;
    struct StackNode sentinel = {NULL, NULL};
    struct StackNode *to_query = mem_alloc(sizeof(*to_query));
    to_query->data = qtree;
    to_query->prev = &sentinel;
    while (to_query->prev)
    {
        struct Quadtree *pointer = to_query->data;
        struct StackNode *to_free = to_query;
        to_query = to_query->prev;
        mem_free(to_free);
        if (pointer->is_node)
        {         
            if (!(pointer->min_x > max_x || pointer->max_x < min_x ||
                  pointer->min_y > max_y || pointer->max_y < min_y))
                {
                    struct StackNode *nw = mem_alloc(sizeof(*nw));
                    nw->data = pointer->NW;
                    nw->prev = to_query;
                    struct StackNode *sw = mem_alloc(sizeof(*sw));
                    sw->data = pointer->SW;
                    sw->prev = nw;
                    struct StackNode *ne = mem_alloc(sizeof(*ne));
                    ne->data = pointer->NE;
                    ne->prev = sw;
                    struct StackNode *se = mem_alloc(sizeof(*se));
                    se->data = pointer->SE;
                    se->prev = ne;
                    to_query = se;                  
                }
        }
        else
        {   
            int stop_iteration = pointer->num_elements;
            for (int i = 0; i != stop_iteration; i++)
            {
                struct PointData element = pointer->elements[i];
                double x = element.x;
                double y = element.y;
                if (min_x < x && x < max_x && min_y < y && y < max_y)
                {   
                    struct ResultNode *new_item = mem_alloc(sizeof(*new_item));
                    new_item->x = x;
                    new_item->y = y;
                    new_item->i = element.i;
                    new_item->prev = result;
                    result = new_item;
                }       
            }
        }
    }
    return result;
}

void 
free_quadtree(struct Quadtree *qtree)
{
    if (qtree->is_node) 
    {
        free_quadtree(qtree->NW);
        free_quadtree(qtree->SW);
        free_quadtree(qtree->NE);
        free_quadtree(qtree->SE);
    }
    else 
    {
        mem_free(qtree->elements);
    }
    mem_free(qtree);
}
