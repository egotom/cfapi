import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:async';
import 'dart:convert';

main() => runApp(InitialSetupPage());

class InitialSetupPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "API Pagination",
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.green),
      home: HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int pageNum = 1;
  bool isPageLoading = false;
  List<Map> arrayOfProducts;
  ScrollController controller;
  Future<List<Map>> future;
  int totalRecord = 0;

  @override
  void initState() {
    controller = new ScrollController()..addListener(_scrollListener);
    future = _callAPIToGetListOfData();

    super.initState();
  }

  @override
  void dispose() {
    controller.removeListener(_scrollListener);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final constListView = ListView.builder(
        itemCount: arrayOfProducts == null ? 0 : arrayOfProducts.length,
        controller: controller,
        physics: AlwaysScrollableScrollPhysics(),
        itemBuilder: (context, index) {
          return Column(
            children: <Widget>[
              ListTile(title: Text('${arrayOfProducts[index]["description"]}')),
              Container(
                color: Colors.black12,
                height: (index == arrayOfProducts.length-1 && totalRecord > arrayOfProducts.length) ? 50 : 0,
                width: MediaQuery.of(context).size.width,
                child:Center(
                  child: CircularProgressIndicator()
                ),
              )
            ],
          );
        });
    return Scaffold(
        appBar: AppBar(title: Text("Online Products"),centerTitle: true),
        body: Container(
          child: FutureBuilder<List<Map>>(
            future: future,
            builder: (BuildContext context, AsyncSnapshot snapshot) {
              switch (snapshot.connectionState) {
                case ConnectionState.none:
                case ConnectionState.active:
                case ConnectionState.waiting:
                  return Center(child: CircularProgressIndicator());
                case ConnectionState.done:
                  if (snapshot.hasError) {
                    Text('YOu have some error : ${snapshot.hasError.toString()}');
                  } else if (snapshot.data != null) {
                    isPageLoading = false;
                    print(arrayOfProducts);
                    return constListView;
                  }
              }
            }),
        ));
  }

  Future<List<Map>> _callAPIToGetListOfData() async {
    isPageLoading = true;
    Map<String, String> headers = {'Accept': 'application/json'};
    final response =await http.get('http://120.26.118.222:5001/score?page=$pageNum', headers: headers);
    var dicOfRes = json.decode(response.body);
    List<Map> temArr =List<Map>.from(dicOfRes);
    setState(() {
      if (pageNum == 1) {
        totalRecord = dicOfRes.length;
        arrayOfProducts = temArr;
      } else {
        arrayOfProducts.addAll(temArr);
      }
      pageNum++;
    });
    return arrayOfProducts;
  }

  _scrollListener() {
    print('====================================');
    print(pageNum);
    print(controller.position.extentAfter);
    if (controller.position.extentAfter <= 0 && isPageLoading == false) {
      _callAPIToGetListOfData();
    }
  }
}

class Score{
    String appeal;
    int appl;
    String approver_id;
    int beneficiary_id;
    String classify;
    String commit;
    String create_at;
    String description;
    int id;
    int proposer_id;
    String refer;
    int refer_id;
    int score;
    String state;
    String update;
  Score.fromJson(Map<String, dynamic> json)
      :appeal= json['appeal'],                
       appl= json['appl'],
       approver_id= json['approver_id'],
       beneficiary_id= json['beneficiary_id'],
       classify= json['classify'],
       commit= json['commit'],
       create_at= json['create_at'],
       description= json['description'],
       id= json['id'],
       proposer_id= json['proposer_id'],
       refer= json['refer'],
       refer_id= json['refer_id'],
       score= json['score'],
       state= json['state'],
       update= json['update'];
}