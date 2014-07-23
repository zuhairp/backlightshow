var blsServices = angular.module('blsServices', []);

blsServices.factory('ProgramStateService', function(){
    return {frames : []};
});

blsServices.factory('LEDService', ['$http', function($http){
    var ledService = {}; 

    ledService.sendColor = function(color_code){
        $http({
            method:'PUT',
            url: '/controller',
            data: $.param({color:color_code}),
            headers: {'Content-Type': 'application/x-www-form-urlencoded'}        
        });
    }

    ledService.sendProgram = function(frames){
        $http({
            method:'PUT',
            url: '/controller',
            data: $.param({frames:frames}),
            headers: {'Content-Type': 'application/x-www-form-urlencoded'}        
        });
    }


    return ledService;
}]);


blsServices.factory('ColorService', ['$http', function($http){
    var colorService = {
        colors: [],
    }

    colorService.updateColors = function(){
        $http.get('/colors').success(function(data){
            var _tempColors = []
            for(var colorName in data){
                _tempColors.push({
                    name: colorName,
                    hex: '#'+data[colorName],
                });
            }
            colorService.colors = _tempColors;
        });
    }

    colorService.updateColors();
    return colorService;
}]);
