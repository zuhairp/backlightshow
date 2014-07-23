var blsControllers = angular.module('blsControllers', []);

blsControllers.controller('NavigationCtrl', ['$scope', '$location', function($scope, $location){
    $scope.isActive = function(path){
        return path === $location.path();
    }
}]);

blsControllers.controller('BasicViewCtrl', ['$scope', '$http', 'LEDService', 'ColorService', function($scope, $http, LEDService, ColorService){
    
    $scope.ColorService = ColorService;

    $scope.turnOff = function(){
        LEDService.sendColor('black');
    };

    $scope.setColor = function(color){
        LEDService.sendColor(color);
    };

    $scope.chosenColor = "#000080";
    
    // Initialize widgets
    $scope.colorChooser = new jscolor.color($('#color-chooser')[0], {hash:'true'});
    $scope.colorChooser.fromString($scope.chosenColor);



}]);

blsControllers.controller('FancyViewCtrl', ['$scope', 'LEDService', 'ProgramStateService', function($scope, LEDService, ProgramStateService){
    
    $scope.ProgramStateService = ProgramStateService;

    $scope.addFrame = function(){
        ProgramStateService.frames.push({
            color: "#000000",
            duration: 1.0,
            transition: 0.0
        });
    }

    $scope.deleteFrame = function(index){
        ProgramStateService.frames.splice(index, 1);
        $scope.$apply();
    }

    $scope.runProgram = function(){
        LEDService.sendProgram(angular.toJson(ProgramStateService.frames));    
    }
    $scope.stopProgram = function(){
        LEDService.sendColor('black');
    }
}]);
