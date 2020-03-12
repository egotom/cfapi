import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_image/network.dart';
import 'package:http/http.dart' as http;
import 'package:async/async.dart';
import 'package:flutter/foundation.dart';

// note: you'll just need to add 'http' and 'flutter_image' packages to pubspec.yaml

void main() {
  runApp(MaterialApp(
    title: "Movie Searcher",
    debugShowCheckedModeBanner: false,
    theme: ThemeData.dark(),
    home: MoviePage(),
  ));
}

enum MovieLoadMoreStatus { LOADING, STABLE }
const String IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w185";
const MOVIE_API_KEY = "8f**********e2"; // get one!
const BASE_URL = "https://api.themoviedb.org/3/movie/";

class Movie {
  Movie({this.title, this.posterPath, this.id, this.overview, this.voteAverage, this.favored});

  final String title, posterPath, id, overview;
  final String voteAverage;
  bool favored;

  factory Movie.fromJson(Map value) {
    return Movie(
        title: value['title'],
        posterPath: value['poster_path'],
        id: value['id'].toString(),
        overview: value['overview'],
        voteAverage: value['vote_average'].toString(),
        favored: false);
  }
}

class MovieList {
  MovieList({
    this.page,
    this.totalResults,
    this.totalPages,
    this.movies,
  });

  final int page;
  final int totalResults;
  final int totalPages;
  final List<Movie> movies;

  MovieList.fromMap(Map<String, dynamic> value)
      : page = value['page'],
        totalResults = value['total_results'],
        totalPages = value['total_pages'],
        movies = List<Movie>.from(value['results'].map((movie) => Movie.fromJson(movie)));
}

class MovieRepository {
  static Future<MovieList> fetchMovies(int pageNumber) async {
    final response = await http.get(BASE_URL + "popular?api_key=" + MOVIE_API_KEY + "&page=" + pageNumber.toString());
    final Map moviesMap = JsonCodec().decode(response.body);
    final movies = MovieList.fromMap(moviesMap);
    if (movies == null) {
      throw Exception("An error occurred");
    }
    return movies;
  }
}

class MoviePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<MovieList>(
        future: MovieRepository.fetchMovies(1),
        builder: (context, snapshots) {
          if (snapshots.hasError) return Text("Error Occurred");

          switch (snapshots.connectionState) {
            case ConnectionState.waiting:
              return Center(child: CircularProgressIndicator());

            case ConnectionState.done:
              return MovieTile(movies: snapshots.data);

            default:
          }
        });
  }
}

class MovieTile extends StatefulWidget {
  final MovieList movies;

  MovieTile({Key key, this.movies}) : super(key: key);

  @override
  State<StatefulWidget> createState() => MovieTileState();
}

class MovieTileState extends State<MovieTile> {
  MovieLoadMoreStatus loadMoreStatus = MovieLoadMoreStatus.STABLE;
  final ScrollController scrollController = ScrollController();
  List<Movie> movies;
  int currentPageNumber;
  CancelableOperation movieOperation;

  @override
  void initState() {
    movies = widget.movies.movies;
    currentPageNumber = widget.movies.page;
    super.initState();
  }

  @override
  void dispose() {
    scrollController.dispose();
    if (movieOperation != null) movieOperation.cancel();
    super.dispose();
  }

  bool onNotification(ScrollNotification notification) {
    if (notification is ScrollUpdateNotification) {
      if (scrollController.position.maxScrollExtent > scrollController.offset && scrollController.position.maxScrollExtent - scrollController.offset <= 50) {
        if (loadMoreStatus != null && loadMoreStatus == MovieLoadMoreStatus.STABLE) {
          loadMoreStatus = MovieLoadMoreStatus.LOADING;
          movieOperation = CancelableOperation.fromFuture(MovieRepository.fetchMovies(currentPageNumber + 1).then((moviesObject) {
            currentPageNumber = moviesObject.page;
            loadMoreStatus = MovieLoadMoreStatus.STABLE;
            setState(() => movies.addAll(moviesObject.movies));
          }));
        }
      }
    }
    return true;
  }

  @override
  Widget build(BuildContext context) {
    final l = movies.length;
    return NotificationListener(
      onNotification: onNotification,
      child: GridView.builder(
        padding: EdgeInsets.only(
          top: 5.0,
        ),
        // EdgeInsets.only
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          childAspectRatio: 0.85,
        ),
        // SliverGridDelegateWithFixedCrossAxisCount
        controller: scrollController,
        itemCount: movies.length,
        physics: const AlwaysScrollableScrollPhysics(),
        itemBuilder: (_, index) {
          return MovieListTile(movie: movies[index]);
        },
      ), // GridView.builder
    ); // NotificationListener
  }
}

class MovieListTile extends StatelessWidget {
  MovieListTile({this.movie});
  final Movie movie;

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.all(
          Radius.circular(15.0),
        ), // BorderRadius.all
      ), // RoundedRectangleBorder
      color: Colors.white,
      elevation: 5.0,
      child: Stack(
        fit: StackFit.expand,
        children: <Widget>[
          Image(
              image: NetworkImageWithRetry(IMAGE_BASE_URL + movie.posterPath, scale: 0.85), // NetworkImageWithRetry
              fit: BoxFit.fill), // Image
          _MovieFavoredImage(movie: movie),
          Align(
            alignment: Alignment.bottomRight,
            child: Padding(
              padding: EdgeInsets.only(bottom: 5.0, right: 5.0),
              child: Text('Rating : ${movie.voteAverage}'),
            ), // Padding
          ) // Align
        ], //  <Widget>[]
      ), // Stack
    ); // Card
  }
}

class _MovieFavoredImage extends StatefulWidget {
  final Movie movie;
  _MovieFavoredImage({@required this.movie});

  @override
  State<StatefulWidget> createState() => _MovieFavoredImageState();
}

class _MovieFavoredImageState extends State<_MovieFavoredImage> {
  Movie currentMovie;

  @override
  void initState() {
    currentMovie = widget.movie;
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      child: Align(
        alignment: Alignment.topRight,
        child: IconButton(
            icon: Icon(
              currentMovie.favored ? Icons.star : Icons.star_border,
            ), // Icon
            onPressed: onFavoredImagePressed), // IconButton
      ), // Align
    ); // Container
  }

  onFavoredImagePressed() {
    setState(() => currentMovie.favored = !currentMovie.favored);
  }
}
