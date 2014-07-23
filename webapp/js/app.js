'use strict';

var blsApp = angular.module('blsApp', ['ngRoute','blsControllers','blsServices','blsDirectives']);

blsApp.config(['$routeProvider', function($routeProvider){
    $routeProvider.
        when('/basic', {
            templateUrl: '/static/partials/basic-template.html', 
            controller: 'BasicViewCtrl'
        }).
        when('/fancy', {
            templateUrl: '/static/partials/fancy-template.html',
            controller: 'FancyViewCtrl'
        }).
        otherwise({
            redirectTo: '/basic'
        });
}]);
