define(['backbone', 'vent',
        'cookie', 'hash'],

        function( Backbone, vent,
                  cookie, hash){
  'use strict';

  var UserObject = Backbone.Model.extend({
    url     : '/api/v1/user',
    defaults : {
      'username'    : 'User_'+ (''+hash( Date.now() )).substring(0,4),
      'email'       : '',
      'experience'  : 2,
      'created'     : '',

      'feedback_0' : -1,
      'feedback_1' : -1,
      'feedback_2' : -1,
      'feedback_3' : -1,

      'advance'       : false,
      'sel_mode'      : "disease",

      'mturk'       : false,
    },

    initialize : function() {
      if(this.authenticated) {
        this.fetch();
      }
    },

    authenticated: function() {
      //-- Consider them logged in if they are a turker or if
      //-- they have a cookie
      console.log('auth :: ', $.cookie('remember_token'));
      return ( Boolean( $.cookie('remember_token') ) );
    },

  });

  return new UserObject();
});
