#include <stdio.h>
#include "m-list.h"

LIST_DEF(list_uint, unsigned int)      /* Define struct list_uint_t and its methods */

int main(void) {
   list_uint_t list ;             /* list_uint_t has been define above */
   list_uint_init(list);          /* All type needs to be initialized */
   list_uint_push_back(list, 42); /* Push 42 in the list */
   list_uint_push_back(list, 17); /* Push 17 in the list */
   list_uint_it_t it;             /* Define an iterator to scan each one */
   for(list_uint_it(it, list)     /* Start iterator on first element */
       ; !list_uint_end_p(it)     /* Until the end is not reached */
       ; list_uint_next(it)) {    /* Set the iterator to the next element*/
          printf("%d\n",          /* Get a reference to the underlying */
            *list_uint_cref(it)); /* data and print it */
   }
   list_uint_clear(list);         /* Clear all the list */
}
