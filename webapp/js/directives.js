blsDirectives = angular.module('blsDirectives', []);

blsDirectives.directive('colorPicker', function(){
    return{
        restrict: 'A',
        scope: {
          colorModel: '=',
        },
        link: function($scope, $element, $attr){
            var chooser = new jscolor.color($element[0], {hash:true});
            chooser.fromString($scope.colorModel);
        }
    }

});

blsDirectives.directive('frameDirective', function(){ //If you're adding a dependency, fix the brackets!
    return{
        restrict: 'AE',
        templateUrl: '/static/partials/frame-template.html',
        scope: {
            frameModel: '=',
            deletePressed: '&',
        },
        link: function($scope, $element, $attr){
            
            $($element).find(".btn-danger").on('click', function(event){
                $scope.deletePressed();
            }); 
            

        }
    }

});
