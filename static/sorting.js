angular.module('sorting', [])

.controller('MainCtrl', ['$scope', function ($scope) {
    $scope.global_resets = [];
    $scope.global_reset = function () {
        for (var i = 0; i < $scope.global_resets.length; i++) {
            $scope.global_resets[i]();
        };
    };
}])

.controller('BubbleSortCtrl', ['$scope', '$interval', 'util',
  function($scope, $interval, util) {

    $scope.sort = {
      viewList: [], // can't be rearranged, or will mess up the animation
      list: [], // used to lookup item locations, in lieu of primary list
      inner: 0, // inner loop increment
      outer: 0, // outer loop increment
      swapped: false,
      step: function() {
        if (this.list[this.inner + 1].val < this.list[this.inner].val) {
          util.swap(this.list, this.inner, this.inner + 1);
          this.swapped = true;
        }
        this.inner++;
        if (this.inner === this.list.length - this.outer - 1) {
          this.outer++;
          this.inner = 0;
          if (!this.swapped) return true;
          this.swapped = false;
        }
        // return true if sort is done
        return this.outer === this.list.length - 1;
      },
      reset: function() {
        this.viewList = util.randList(10, 10);
        this.list = this.viewList.slice(0);
        this.inner = this.outer = 0;
        this.swapped = this.done = false;
        $interval.cancel(interval);
      }
    };

    var interval;
    $scope.restart = function () {
        $scope.sort.reset();
        interval = $interval(function() {
          if ($scope.sort.step()) {
            $scope.sort.done = true;
            $interval.cancel(interval);
          }
        }, 1000);        
    };
    $scope.restart();
    $scope.global_resets.push($scope.restart);
  }
])

.controller('InsertionSortCtrl', ['$scope', '$interval', 'util',
  function($scope, $interval, util) {

    $scope.sort = {
      viewList: [],
      list: [],
      inc: 1,
      hole: 0,
      holeItem: null,
      setHole: function(index) {
        this.hole = index;
        this.holeItem = this.list[index];
        this.holeItem.hole = true;
      },
      step: function() {
        if (!this.holeItem) {
          this.setHole(this.inc);
        }
        if (this.hole !== 0 && this.holeItem.val < this.list[this.hole - 1].val) {
          util.move(this.list, this.list[this.hole - 1], this.hole);
          this.hole--;
        } else {
          this.holeItem.index = this.hole;
          this.list[this.hole] = this.holeItem;
          this.holeItem.hole = false;
          if (this.inc + 1 > this.list.length) return true;
          this.setHole(this.inc);
          this.inc++;
        }
        return this.inc > this.list.length;
      },
      reset: function() {
        this.viewList = util.randList(10, 10);
        this.list = this.viewList.slice(0);
        this.inc = 1;
        this.hole = 0;
        this.holeItem = null;
        this.done = false;
        $interval.cancel(interval);
      }
    };

    var interval;
    $scope.restart = function () {
        $scope.sort.reset();
        interval = $interval(function() {
          if ($scope.sort.step()) {
            $scope.sort.done = true;
            $interval.cancel(interval);
          }
        }, 1000);        
    };
    $scope.restart();
    $scope.global_resets.push($scope.restart);
  }
])

.controller('SelectionSortCtrl', ['$scope', '$interval', 'util',
  function($scope, $interval, util) {

    $scope.sort = {
      done: false,
      viewList: [],
      list: [],
      outer: 0,
      inner: 0,
      min: 0,
      step: function() {
        if (this.inner === this.list.length - 1) {
          util.swap(this.list, this.outer, this.min);
          if (this.outer === this.list.length - 2) {
            return true;
          }
          this.inner = this.min = ++this.outer;
        }
        this.inner++;
        if (this.list[this.min].val > this.list[this.inner].val) {
          this.min = this.inner;
        }
      },
      reset: function() {
        this.viewList = util.randList(10, 10);
        this.list = this.viewList.slice(0);
        this.inner = this.outer = 0;
        this.done = false;
        $interval.cancel(interval);
      }
    };

    var interval;
    $scope.restart = function () {
        $scope.sort.reset();
        interval = $interval(function() {
          if ($scope.sort.step()) {
            $scope.sort.done = true;
            $interval.cancel(interval);
          }
        }, 1000);        
    };
    $scope.restart();
    $scope.global_resets.push($scope.restart);
  }
])

.controller('MergeSortCtrl', ['$scope', '$interval', 'util',
  function($scope, $interval, util) {

    $scope.pow = Math.pow;

    $scope.sort = {
      done: false,
      viewList: [],
      list: [],
      sublists: [],
      curLevel: 0,
      merging: false,
      step: function() {
        if (this.merging) {
          return this.merge();
        } else {
          return this.split();
        }
      },
      split: function() {
        var list = null;
        for (var i = 0; i < this.sublists.length; i++) {
          if (this.sublists[i].length === this.list.length / Math.pow(2, this.curLevel)) {
            list = this.sublists.splice(i, 1)[0];
            break;
          }
        }
        var left = list.slice(0, list.length / 2);
        var right = list.slice(list.length / 2);
        this.setLevel(left, this.curLevel + 1, i);
        this.setLevel(right, this.curLevel + 1, i + 1);
        if (this.sublists.length === this.list.length) {
          this.merging = true;
        } else if (i + 2 === this.sublists.length) {
          this.curLevel++;
        }
      },
      left: [],
      right: [],
      curLevelSize: 0,
      merge: function() {
        if (!this.left.length && !this.right.length) {
          this.left = this.sublists.splice(0, 1)[0];
          this.right = this.sublists.splice(0, 1)[0];
          this.sublists.push([]);
        }
        var targetList = this.sublists[this.sublists.length - 1];
        if (this.left.length && this.right.length) {
          if (this.left[0].val <= this.right[0].val) {
            this.mergeListHead(this.left, targetList, this.curLevelSize++);
          } else {
            this.mergeListHead(this.right, targetList, this.curLevelSize++);
          }
        } else if (this.left.length) {
          this.mergeListHead(this.left, targetList, this.curLevelSize++);
        } else if (this.right.length) {
          this.mergeListHead(this.right, targetList, this.curLevelSize++);
        }

        if (this.sublists[0].length === this.list.length) {
          return true;
        } else if (this.curLevelSize === this.list.length) {
          this.curLevelSize = 0;
          this.curLevel--;
        }
      },
      mergeListHead: function(list, targetList, index) {
        list[0].index = index;
        list[0].level = this.curLevel;
        list[0].sublist = Math.pow(2, this.curLevel + 1) - this.sublists.length - 1;
        targetList.push(list.shift());
      },
      setLevel: function(itemList, level, sublist) {
        for (var i = 0; i < itemList.length; i++) {
          itemList[i].level = level;
          itemList[i].sublist = sublist;
        }
        this.sublists.splice(sublist, 0, itemList);
      },
      reset: function() {
        this.viewList = util.randList(8, 10);
        this.list = this.viewList.slice(0);
        this.sublists = [];
        this.setLevel(this.list, 0, 0);
        this.done = this.merging = false;
        this.left = [];
        this.right = [];
        this.curLevel = this.curLevelSize = 0;
        $interval.cancel(interval);
      },
    };

    var interval;
    $scope.restart = function () {
        $scope.sort.reset();
        interval = $interval(function() {
          if ($scope.sort.step()) {
            $scope.sort.done = true;
            $interval.cancel(interval);
          }
        }, 1000);        
    };
    $scope.restart();
    $scope.global_resets.push($scope.restart);
  }
])


/* SERVICES */
.service('util', [
  function() {

    return {
      // Due the nature of the animation, we can't move things in the main list.
      // This swap function is meant to change an item's location in a secondary 
      // list and set an index property that is used in the view
      swap: function(list, i1, i2) {
        var temp = list[i1];
        list[i1] = list[i2];
        list[i2] = temp;

        list[i2].index = i2;
        list[i1].index = i1;
      },
      move: function(list, item, index) {
        item.index = index;
        list[index] = item;
      },
      randList: function(length, max) {
        var result = [];
        for (var i = 0; i < length; i++) {
          var val = Math.ceil(Math.random() * max);
          result.push({
            val: val,
            index: i
          });
        }
        return result;
      }
    };

  }
])

/* DIRECTIVES */
.directive('ynHeight', ['$parse',
  function($parse) {
    return {
      restrict: 'A',
      link: function(scope, element, attrs /*, ctrl*/ ) {
        scope.$watch(attrs.ynHeight, function(val) {
          element.css('height', val + 'px');
        });
      }
    };
  }
])

.directive('ynWidth', ['$parse',
  function($parse) {
    return {
      restrict: 'A',
      link: function(scope, element, attrs /*, ctrl*/ ) {
        scope.$watch(attrs.ynWidth, function(val) {
          element.css('width', val + 'px');
        });
      }
    };
  }
])

.directive('ynTop', ['$parse',
  function($parse) {
    return {
      restrict: 'A',
      link: function(scope, element, attrs /*, ctrl*/ ) {
        scope.$watch(attrs.ynTop, function(val) {
          element.css('top', val + 'px');
        });
      }
    };
  }
])

.directive('ynLeft', ['$parse',
  function($parse) {
    return {
      restrict: 'A',
      link: function(scope, element, attrs /*, ctrl*/ ) {
        scope.$watch(attrs.ynLeft, function(val) {
          element.css('left', val + 'px');
        });
      }
    };
  }
]);