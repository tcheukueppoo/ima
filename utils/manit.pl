#!/usr/bin/env perl

use strict;
use warnings;
use feature qw(say);

use List::Util qw(max);

sub get_options {
   my ( %options, $option );

   local $/;
   open my $fh, '<', '../src/ima/options.py' or die $!;
   $_ = <$fh>;
   {
      if ( m/\G.*?\s*parser[.]add_option[(]\s*'(?<o>-\w)'\s*,\s*(?:'--(?<o>\w+(?:(?>-\w+)+)?)',)?\s*/g ) {
         $option = join ' ', @{$-{o}};
         redo;
      }

      if ( m/\G.*?help\s*=\s*'(?<d>.+?)'\s*/g ) {
         $options{$option}{d} = $+{d};
         {
            if ( m/\G\s+'(?<d>.+?)'\s*/g ) {
               $options{$option}{d} .= $+{d};
               redo;
            }
         }
         redo;
      }

      if ( m/\G.*?\s+metavar\s*=\s*'(?<v>.+?)'\s*,/g ) {
         $options{$option}{v} = $+{v};
         redo;
      }
   }

   return %options;
}

sub output_doc_options {
   my %options = shift;

   say '> Mandatory arguments to long options are mandatory for short options too.';
   foreach my $option ( keys %options ) {
      printf '> **%s**\n', $option;
      printf '>> %s\n', $options{$option};
   }
}

sub output_synopsis {
   my %options  = shift;
   my $synopsis = join ' ', map '[ ' . ( $_ =~ s/ /|/r ) . ( $options{$_}{v} // '' =~ s/(.+)/**$1**/r ) . ']', keys %options;

   say "# SYNOPSIS";
   printf '> **ima** %s **QUERY** [..QUERY]\n\n', $synopsis
   say;
}

sub output_authors {
   open my $fh, '<', '../AUTHORS.md' or die $!;

   say "# AUTHORS"
   while ( <$fh> ) {
      printf '> %s\n', $1 if m/^\* (.+)$/;
   }
   say;
}

sub output_file {
   my $file = shift;

   open my $fh, '<', $file or die $!;
   say while <$fh>;
   say;
}

output_heading('./heading.md');
%options = get_options();
output_synopsis( %options );
output_doc_options( %options );

output_file('./body.md');
output_authors();
output_file('./issues.md');
output_file('./license.md');
