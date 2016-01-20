/*
 *  Models & Collections
 */
Relation = Backbone.RelationalModel.extend({
  defaults: {
    id: '',
    text: '',
    selected: false
  },

  relations: [{
    type: 'HasMany',
    key: 'children',

    relatedModel: 'Relation',
    collectionType: 'RelationList',

    reverseRelation : {
      key : 'parentRelation',
      includeInJSON: false,
    }
  }],

  get_selected: function() {
    /* Try to find an instance of 'this' model type in the store */
    var model = Backbone.Relational.store.find( this, {"selected": true});
    console.log('model:', model);

    if ( !model && _.isObject( attributes ) ) {
      var coll = Backbone.Relational.store.getCollection( this );

      model = coll.find( function( m ) {
        return m.selected === true;
      });
    }
    return model;
  }

});

RelationList = Backbone.Collection.extend({
  model: Relation,
  url: '/api/v1/words',
});

function get_stype(the_current_relation) {
  return $(this).hasClass('.gene');
};
/*
 * Views
 */
RelationView = Backbone.Marionette.ItemView.extend({
  template: _.template('<%= text %>'),
  tagName: 'a',
  className: 'list-group-item',

  events : {
    'mousedown' : 'mousedown',
  },

  mousedown : function(evt) {
    /*
     * 1. Set the current choice to the ID
     * 2. Set the backbutton reference if available
     * 3. Set the list updated to any children
     *
     */
    var children = this.model.get('children');
    Tree['convoChannel'].trigger('click', {'collection': children, 'choice': this.model});
  },
});


RelationCompositeView = Backbone.Marionette.CompositeView.extend({
  template: '#tree-template',
  templateHelpers: function() {
    return this.options.concepts
  },

  childView  : RelationView,
  childViewContainer: "ul",
  /*
  tagName   : 'div',
  className : 'paragraph',
  */

  ui: {
    'c1': '#c1',
    'c1_fade_in': '.fade_in',
    'relation': '#relation',
    'c2': '#c2',
    'c2_fade_in': '.fade_in',
    'c1_not_correct': '#c1_not_correct',
    'c2_not_correct': '#c2_not_correct',
    'submit_button': '#submit_button'
  },

  events : {
    'mousedown @ui.relation': 'resetRelationship',
    'mousedown @ui.c1_not_correct': 'c1Error',
    'mousedown @ui.c2_not_correct': 'c2Error',
    'mousedown @ui.submit_button': 'submit_fade_in',
  },

  resetRelationship: function(evt) {
    Tree['convoChannel'].trigger('back', this.options);
  },

  c1Error: function(evt) {
    Tree['convoChannel'].trigger('error', 'c_1');
  },
  c2Error: function(evt) {
    Tree['convoChannel'].trigger('error', 'c_2');
  },

  submit_fade_in: function(evt){
    console.log('submit fade in');
    this.ui.c1.fadeIn(1000);
    this.ui.c2.fadeIn(1000);
  },


  onRender : function() {
    var self = this;
    var choice = this.options['choice'];
    var concepts = this.options['concepts'];
    /*
     * console.log('[RelationCompositeView onRender] Choice:', choice);
     */

    if(choice) {
      this.ui.relation.removeClass('disabled').text( choice.get('text') );
    }

    // this.ui.c1_fade_in.fadeIn(1000);
    // this.ui.c2_fade_in.fadeIn(1000);

    // this.ui.c1.fadeIn(1000);
    // this.ui.c2.fadeIn(1000);

    this.ui.c1.mouseenter(function () {
      $(this).addClass("not-correct-concept");
    });

    this.ui.c2.mouseenter(function () {
      $(this).addClass("not-correct-concept");
    });

    if(choice || this.collection.parentRelation) {
      this.ui.relation.removeClass('disabled');
      self.ui.relation.addClass('relation-go-back');
    }

  }
});

Tree = new Backbone.Marionette.Application();