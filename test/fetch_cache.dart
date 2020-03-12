import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';

void main() => runApp(new MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return new MaterialApp(
      title: 'Flutter Demo',
      theme: new ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: new MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => new _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  var cacheddata = new Map<int, Data>();
  var offsetLoaded = new Map<int, bool>();
  int _total = 0;

  @override
  void initState() {
    _getTotal().then((int total) {
      setState(() {
        _total = total;
      });
    });
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    var listView = ListView.builder(
        itemCount: _total,
        itemBuilder: (BuildContext context, int index) {
          Data data = _getData(index);
          return ListTile(
            title: Text(data.value),
          );
        }
    );

    return Scaffold(
      appBar: AppBar(
        title: Text("App Bar Title"),
      ),
      body: listView,
    );
  }

  Future<List<Data>> _getDatas(int offset, int limit) async {
    String json = await _getJson(offset, limit);
    List<Map> list = JSON.decode(json);
    var datas = new List<Data>();
    list.forEach((Map map) => datas.add(new Data.fromMap(map)));
    return datas;
  }

  Future<String> _getJson(int offset, int limit) async {
    String json = "[";
    for (int i= offset; i < offset + limit; i++) {
      String id = i.toString();
      String value = "value ($id)";
      json += '{ "id":"$id", "value":"$value" }';
      if (i < offset + limit - 1) {
        json += ",";
      }
    }
    json += "]";
    await new Future.delayed(new Duration(seconds: 3));
    return json;
  }

  Data _getData(int index) {
    Data data = cacheddata[index];
    if (data == null) {
      int offset = index ~/ 5 * 5;
      if (!offsetLoaded.containsKey(offset)) {
        offsetLoaded.putIfAbsent(offset, () => true);
        _getDatas(offset, 5).then((List<Data> datas) => _updateDatas(offset, datas));
      }
      data = new Data.loading();
    }
    return data;
  }

  Future<int> _getTotal() async {
    return 1000;
  }

  void _updateDatas(int offset, List<Data> datas) {
    setState((){
      for (int i=0; i < datas.length; i++) {
        cacheddata.putIfAbsent(offset + i, () => datas[i]);
      }
    });
  }
}

class Data {
  String id;
  String value;

  Data.loading() {
    value = "Loading...";
  }

  Data.fromMap(Map map) {
    id = map['id'];
    value = map['value'];
  }
}