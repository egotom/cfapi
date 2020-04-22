import 'package:cfapi/config/theme.dart';
import 'package:flutter/material.dart';
import 'package:charts_flutter/flutter.dart' as charts;

class MyRank extends StatelessWidget {
  final List<charts.Series> seriesList;
  final bool animate;

  MyRank(this.seriesList, {this.animate});
  factory MyRank.withSampleData() {
    return MyRank(
      _createSampleData(),
      animate: false,
    );
  }
  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(      
      child: Column(
        children: <Widget>[
          Row(
            children: <Widget>[
              Expanded(
                child: Card(
                  color:MyTheme().scdc,
                  child: InkWell(
                    splashColor: Colors.white.withAlpha(80),
                    child: Container(                      
                      width: 100,
                      height: 100,
                      padding: EdgeInsets.symmetric(vertical:0.0,horizontal:5.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: <Widget>[
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: <Widget>[
                              Text('月积分: ' ,style:MyTheme().scdf),
                              Text('月排名: ' ,style:MyTheme().scdf),
                              Text('团队排名: ' ,style:MyTheme().scdf),
                            ],
                          ),
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: <Widget>[
                              Text('--' ,style:MyTheme().scdf),
                              Text('--' ,style:MyTheme().scdf),
                              Text('--' ,style:MyTheme().scdf),
                            ],
                          ),
                        ],
                      ),
                    ),
                  )
                ),
              ),
              Expanded(
                child: Card(
                  color:MyTheme().scdc,
                  child: InkWell(
                    splashColor: Colors.white.withAlpha(80),
                    child: Container(
                      width: 100,
                      height: 100,
                      padding: EdgeInsets.symmetric(vertical:0.0,horizontal:5.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: <Widget>[
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: <Widget>[
                              Text('年积分:' ,style:MyTheme().scdf),
                              Text('年排名:' ,style:MyTheme().scdf),
                              Text('团队排名:' ,style:MyTheme().scdf),
                            ],
                          ),
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: <Widget>[
                              Text('--' ,style:MyTheme().scdf),
                              Text('--' ,style:MyTheme().scdf),
                              Text('--' ,style:MyTheme().scdf),
                            ],
                          ),
                        ],
                      ),
                    ),
                  )
                ),
              ),
              Expanded(
                child: Card(
                  color:MyTheme().scdc,
                  child: InkWell(
                    splashColor: Colors.white.withAlpha(80),
                    child: Container(
                      width: 100,
                      height: 100,
                      padding: EdgeInsets.symmetric(vertical:0.0,horizontal:5.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: <Widget>[
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: <Widget>[
                              Text('累计积分:' ,style:MyTheme().scdf),
                              Text('累计排名:' ,style:MyTheme().scdf),
                              Text('团队排名:' ,style:MyTheme().scdf),
                            ],
                          ),
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: <Widget>[
                              Text('--' ,style:MyTheme().scdf),
                              Text('--' ,style:MyTheme().scdf),
                              Text('--' ,style:MyTheme().scdf),
                            ],
                          ),
                        ],
                      ),
                    ),
                  )
                ),
              ),
            ],
          ),
          SizedBox(height:20),
        ],
      ),
    );
  }
  static List<charts.Series<LinearSales, int>> _createSampleData() {
    final data = [
      LinearSales(0, 5),
      LinearSales(1, 25),
      LinearSales(2, 100),
      LinearSales(3, 75),
    ];

    return [
      charts.Series<LinearSales, int>(
        id: 'Sales',
        colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
        domainFn: (LinearSales sales, _) => sales.year,
        measureFn: (LinearSales sales, _) => sales.sales,
        data: data,
      )
    ];
  }
}

class LinearSales {
  final int year;
  final int sales;
  LinearSales(this.year, this.sales);
}