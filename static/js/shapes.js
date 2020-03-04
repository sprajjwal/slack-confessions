$(document).ready(function(){
  
  var background = {
    initialize : function (){
      
      this.id = "my_background";
      this.style = {
        bubbles_color : "white",
        stroke_width : 0,
        stroke_color : "black"
      };
      this.bubbles_number = 25;
      this.speed = [1500 , 8000];
      this.max_bubbles_height = this.height;
      this.shape = false;
      
      if($("#"+ this.id).length > 0){
        $("#" + this.id).remove();
      }
      
      this.object = $("<div style='z-index:1;margin:0;padding:0;overflow:hidden;position:absolute;bottom:0;' id='" + this.id + "'></div>'").appendTo('body');
      
      this.ww = $(window).width();
      this.wh = $(window).height();
      this.width = this.object.width(this.ww);
      this.height = this.object.height(this.wh + 200);
      
      $('body').prepend("<style> .shape-background{transform-origin:center; width:80px; height:80px; background:" + this.style.bubbles_color + "; position:absolute}</style>");
      
      for (i=0; i<this.bubbles_number; i++){
        this.generate_bubbles();
      }
    },
    
    generate_bubbles: function(){
      var $this = this;
      var base = $("<div class='shape-background'></div>");
      var shape_type = $this.shape ? $this.shape : Math.floor($this.rn(1,3));
      
      if(shape_type == 1){
        var bolla = base.css({borderRadius: "50%"});
      }
      else if(shape_type == 2){
      var bolla = base.css({
        width: 0,
        height: 0,
        "border-style": "solid",
        "border-width": "0 40px 69.3px 40px",
        "border-color":
          "transparent transparent " + $this.style.bubbles_color + " transparent",
        background: "transparent"
      });
      }
      else{
        var bolla = base;
      }
      
      var rn_size = $this.rn(0.8,1.2);
      
      bolla.css({
        transform: "scale("+ rn_size +")rotate("+ $this.rn(-360,360)+ "deg)",
        top:$this.wh + 300,
        left: $this.rn(-60 , $this.ww + 60)
      });
      
      bolla.appendTo($this.object);
      //for super smooth transitions and transformations we included the transit tool
      bolla.transit({
        top:$this.rn($this.wh/2, $this.wh/2, -60),
        transform : "scale("+ rn_size +") rotate(" + $this.rn(-360,360)+"deg)",
        opacity:0
      },
       $this.rn($this.speed[0],$this.speed[1]),
                   function(){
        $(this).remove();
        $this.generate_bubbles();
      }
      );
    },
    
    rn :function(from , to , arr){
    if(arr){
      return Math.random()*(to - from + 1) + from;
    }
      else{
        return Math.floor(Math.random()*(to - from + 1) + from);
      }
  }
  };
  
  background.initialize();
    
  });