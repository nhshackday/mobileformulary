$(document).ready(function (){
  //open links with js to stop iphone app stupidness: http://stackoverflow.com/questions/2898740/iphone-safari-web-app-opens-links-in-new-window
  $("a").click(function (event) {
      event.preventDefault();
      window.location = $(this).attr("href");
  });

  //open close details
  $('.drug h2').click(function (event){
      if($(this).next().is(":hidden")){
        $(this).next().slideDown();
      }else{
         $(this).next().slideUp();
      }
   });

});

//setup iphone bookmark prompt
 window.addEventListener('load', function() {
   window.setTimeout(function() {
     var bubble = new google.bookmarkbubble.Bubble();

     var parameter = 'bmb=1';

     bubble.hasHashParameter = function() {
       return window.location.hash.indexOf(parameter) != -1;
     };

     bubble.setHashParameter = function() {
       if (!this.hasHashParameter()) {
         window.location.hash += parameter;
       }
     };

     bubble.getViewportHeight = function() {
       window.console.log('Example of how to override getViewportHeight.');
       return window.innerHeight;
     };

     bubble.getViewportScrollY = function() {
       window.console.log('Example of how to override getViewportScrollY.');
       return window.pageYOffset;
     };

     bubble.registerScrollHandler = function(handler) {
       window.console.log('Example of how to override registerScrollHandler.');
       window.addEventListener('scroll', handler, false);
     };

     bubble.deregisterScrollHandler = function(handler) {
       window.console.log('Example of how to override deregisterScrollHandler.');
       window.removeEventListener('scroll', handler, false);
     };

     bubble.showIfAllowed();
   }, 1000);
 }, false);
